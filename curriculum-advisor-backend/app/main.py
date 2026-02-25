from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
from app.services.graduation_audit import run_graduation_audit
from app.services.grading import is_passing
from .db import get_db
from .models import AdvisingSession, SessionCourseAttempt
from .schemas import (
    CreateSessionRequest,
    CreateSessionResponse,
    TranscriptRow,
    TrackSelectRequest,
    RecommendationRequest,   # ← added
)
from .services.advising import build_recommendations


app = FastAPI(title="Curriculum Advisor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------
# Create Advising Session
# ----------------------------
@app.post("/advising-session", response_model=CreateSessionResponse)
def create_advising_session(payload: CreateSessionRequest, db: Session = Depends(get_db)):
    curriculum_id = db.execute(text("""
        SELECT curriculum_id
        FROM curriculum_id_ranges
        WHERE :sid BETWEEN id_start AND id_end
        LIMIT 1
    """), {"sid": payload.student_id_number}).scalar()

    if not curriculum_id:
        raise HTTPException(status_code=404, detail="No curriculum found for this student_id_number")

    session_row = AdvisingSession(
        student_id_number=payload.student_id_number,
        curriculum_id=curriculum_id,
        earned_credits=0
    )
    db.add(session_row)
    db.commit()
    db.refresh(session_row)

    return CreateSessionResponse(
        session_id=session_row.session_id,
        curriculum_id=curriculum_id
    )


@app.post("/advising-session/{session_id}/transcript")
def upload_transcript(session_id: int, rows: list[TranscriptRow], db: Session = Depends(get_db)):
    session_row = db.get(AdvisingSession, session_id)
    if not session_row:
        raise HTTPException(status_code=404, detail="Session not found")

    # Clear previous attempts (optional but recommended)
    db.execute(
        text("DELETE FROM session_course_attempts WHERE session_id = :sid"),
        {"sid": session_id}
    )

    total_earned = 0

    for r in rows:

        # 1️⃣ Find course_code_id + official credits + seminar flag
        course_row = db.execute(text("""
            SELECT 
                cc.course_code_id,
                c.course_id,
                c.credits,
                c.is_ethics_seminar
            FROM course_codes cc
            JOIN courses c ON c.course_id = cc.course_id
            WHERE cc.course_code = :code
        """), {"code": r.course_code}).mappings().first()

        if not course_row:

            free_row = db.execute(text("""
                SELECT cc.course_code_id, c.credits
                FROM course_codes cc
                JOIN courses c ON c.course_id = cc.course_id
                WHERE cc.course_code = 'FREE_ELECTIVE'
                LIMIT 1
            """)).mappings().first()

            if not free_row:
                raise HTTPException(status_code=500, detail="FREE_ELECTIVE not configured")

            grade = r.grade.strip().upper()
            earned = 0

            if grade not in ["F", "W", "IP"]:
                earned = int(free_row["credits"])

            db.add(SessionCourseAttempt(
                session_id=session_id,
                course_code_id=free_row["course_code_id"],
                grade=grade,
                credits_earned=earned,
                term=r.term
            ))

            total_earned += earned
            continue
        course_code_id = course_row["course_code_id"]
        official_credits = int(course_row["credits"])
        is_seminar = course_row["is_ethics_seminar"]

        grade = r.grade.strip().upper()

        earned = 0

        # 2️⃣ Seminar rule
        if is_seminar:
            if grade == "S":
                earned = 0  # seminar gives 0 credits
            else:
                earned = 0

        # 3️⃣ TR always pass
        elif grade == "TR":
            earned = official_credits

        # 4️⃣ IP / W / F do not count
        elif grade in ["IP", "W", "F"]:
            earned = 0

        # 5️⃣ Normal grade logic (A B C D)
        else:
            # get required minimum grade from DB
            required_row = db.execute(text("""
                SELECT COALESCE(min_required_grade::text, 'D') AS required_grade
                FROM curriculum_course_min_grades
                WHERE curriculum_id = :cid
                  AND course_id = :course_id
            """), {
                "cid": session_row.curriculum_id,
                "course_id": course_row["course_id"]
            }).mappings().first()

            required_grade = required_row["required_grade"] if required_row else "D"

            # Use your existing helper
            if is_passing(grade, required_grade):
                earned = official_credits
            else:
                earned = 0

        # 6️⃣ Store attempt
        db.add(SessionCourseAttempt(
            session_id=session_id,
            course_code_id=course_code_id,
            grade=grade,
            credits_earned=earned,
            term=r.term
        ))

        total_earned += earned

    # 7️⃣ Update session total credits
    db.execute(text("""
        UPDATE advising_sessions
        SET earned_credits = :total
        WHERE session_id = :sid
    """), {
        "total": total_earned,
        "sid": session_id
    })

    db.commit()

    return {
        "session_id": session_id,
        "rows_inserted": len(rows),
        "total_earned_credits": total_earned
    }


# ----------------------------
# Set Concentration
# ----------------------------
@app.post("/advising-session/{session_id}/concentration")
def set_concentration(session_id: int, payload: TrackSelectRequest, db: Session = Depends(get_db)):
    curriculum_id = db.execute(
        text("SELECT curriculum_id FROM advising_sessions WHERE session_id = :sid"),
        {"sid": session_id}
    ).scalar()

    if not curriculum_id:
        raise HTTPException(status_code=404, detail="Session not found")

    ok = db.execute(text("""
        SELECT 1
        FROM major_elective_groups
        WHERE group_id = :gid AND curriculum_id = :cid
        LIMIT 1
    """), {"gid": payload.group_id, "cid": curriculum_id}).scalar()

    if not ok:
        raise HTTPException(status_code=400, detail="Invalid group_id for this curriculum")

    db.execute(text("""
        INSERT INTO session_concentration_selection (session_id, group_id)
        VALUES (:sid, :gid)
        ON CONFLICT (session_id) DO UPDATE
        SET group_id = EXCLUDED.group_id,
            selected_at = NOW()
    """), {"sid": session_id, "gid": payload.group_id})

    db.commit()

    return {
        "session_id": session_id,
        "group_id": payload.group_id
    }


# ----------------------------
# Get Recommendations + Semester Plan
# ----------------------------
@app.post("/advising-session/{session_id}/recommendations")
def get_recommendations(
    session_id: int,
    payload: RecommendationRequest,
    db: Session = Depends(get_db)
):
    result = build_recommendations(
        session_id=session_id,
        db=db,
        max_credits=payload.max_credits,
        offered_courses=payload.offered_courses
    )

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


# ----------------------------
# Graduation Audit
# ----------------------------
@app.get("/advising-session/{session_id}/graduation-audit")
def graduation_audit(session_id: int, db: Session = Depends(get_db)):
    return run_graduation_audit(session_id=session_id, db=db)

# ============================================================
# ADMIN COURSE CRUD
# ============================================================

from pydantic import BaseModel
from typing import List


# ----------------------------
# Admin Schemas
# ----------------------------

class CourseCreate(BaseModel):
    course_name: str
    credits: int
    is_ethics_seminar: bool = False
    is_active: bool = True


class CourseUpdate(BaseModel):
    course_name: str
    credits: int
    is_ethics_seminar: bool
    is_active: bool


# ----------------------------
# Get All Courses
# ----------------------------

@app.get("/admin/courses")
def get_all_courses(db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT 
            course_id,
            course_name,
            credits,
            is_ethics_seminar,
            is_active
        FROM courses
        ORDER BY course_id
    """)).mappings().all()

    return rows


# ----------------------------
# Create Course
# ----------------------------

@app.post("/admin/courses")
def create_course(payload: CourseCreate, db: Session = Depends(get_db)):
    new_id = db.execute(text("""
        INSERT INTO courses (
            course_name,
            credits,
            is_ethics_seminar,
            is_active
        )
        VALUES (
            :name,
            :credits,
            :seminar,
            :active
        )
        RETURNING course_id
    """), {
        "name": payload.course_name,
        "credits": payload.credits,
        "seminar": payload.is_ethics_seminar,
        "active": payload.is_active
    }).scalar()

    db.commit()

    return {
        "message": "Course created successfully",
        "course_id": new_id
    }


# ----------------------------
# Update Course
# ----------------------------

@app.put("/admin/courses/{course_id}")
def update_course(course_id: int, payload: CourseUpdate, db: Session = Depends(get_db)):
    db.execute(text("""
        UPDATE courses
        SET
            course_name = :name,
            credits = :credits,
            is_ethics_seminar = :seminar,
            is_active = :active
        WHERE course_id = :cid
    """), {
        "cid": course_id,
        "name": payload.course_name,
        "credits": payload.credits,
        "seminar": payload.is_ethics_seminar,
        "active": payload.is_active
    })

    db.commit()

    return {"message": "Course updated successfully"}