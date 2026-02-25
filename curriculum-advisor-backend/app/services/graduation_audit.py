# app/services/graduation_audit.py

from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any

from .grading import is_passing


def run_graduation_audit(session_id: int, db: Session) -> Dict[str, Any]:
    """
    Graduation audit engine.
    Checks:
    1) Total earned credits
    2) Main category credit requirements
    3) Professional Ethics Seminar completion (S only)
    """

    # --------------------------------------------------
    # 1) Load advising session
    # --------------------------------------------------
    session_row = db.execute(
        text("""
            SELECT session_id, curriculum_id
            FROM advising_sessions
            WHERE session_id = :sid
        """),
        {"sid": session_id}
    ).mappings().first()

    if not session_row:
        return {"error": "Session not found"}

    curriculum_id = int(session_row["curriculum_id"])

    # --------------------------------------------------
    # 2) Load passed courses + required grade
    # --------------------------------------------------
    attempts = db.execute(text("""
        SELECT
            a.grade,
            cc.course_code,
            cc.course_code_id,
            c.course_id,
            c.credits,
            c.is_ethics_seminar,
            COALESCE(mg.min_required_grade::text, 'D') AS required_grade
        FROM session_course_attempts a
        JOIN course_codes cc ON cc.course_code_id = a.course_code_id
        JOIN courses c ON c.course_id = cc.course_id
        LEFT JOIN curriculum_course_min_grades mg
            ON mg.curriculum_id = :cid
            AND mg.course_id = c.course_id
        WHERE a.session_id = :sid
    """), {"sid": session_id, "cid": curriculum_id}).mappings().all()

    passed_course_ids = set()
    earned_credits = 0

    for row in attempts:
        # Seminar rule: only grade 'S' counts
        if row["is_ethics_seminar"]:
            if row["grade"] == "S":
                passed_course_ids.add(int(row["course_id"]))
        else:
            if is_passing(row["grade"], row["required_grade"]):
                passed_course_ids.add(int(row["course_id"]))
                earned_credits += int(row["credits"])

    # --------------------------------------------------
    # 3) Load total required credits
    # --------------------------------------------------
    total_required_row = db.execute(text("""
        SELECT total_required_credits
        FROM curriculums
        WHERE curriculum_id = :cid
    """), {"cid": curriculum_id}).mappings().first()

    total_required = int(total_required_row["total_required_credits"])
    total_remaining = max(0, total_required - earned_credits)
    total_status = "COMPLETED" if total_remaining == 0 else "INCOMPLETE"

    percentage = round((earned_credits / total_required) * 100, 2) if total_required > 0 else 0

    # --------------------------------------------------
    # 4) Main Category Credit Audit
    # --------------------------------------------------
    required_by_category = {}

    required_rows = db.execute(text("""
        SELECT 
            mc.name AS main_category,
            cmc.required_credits
        FROM curriculum_main_categories cmc
        JOIN main_categories mc 
            ON mc.main_category_id = cmc.main_category_id
        WHERE cmc.curriculum_id = :cid
    """), {"cid": curriculum_id}).mappings().all()

    for row in required_rows:
        required_by_category[row["main_category"]] = int(row["required_credits"])

    earned_by_category = {}

    category_credit_rows = db.execute(text("""
        SELECT 
            mc.name AS main_category,
            SUM(c.credits) AS earned_credits
        FROM session_course_attempts a
        JOIN course_codes cc ON cc.course_code_id = a.course_code_id
        JOIN courses c ON c.course_id = cc.course_id
        JOIN subcategory_course_codes sc ON sc.course_code_id = cc.course_code_id
        JOIN curriculum_subcategories sub ON sub.subcategory_id = sc.subcategory_id
        JOIN main_categories mc ON mc.main_category_id = sub.main_category_id
        WHERE a.session_id = :sid
          AND sub.curriculum_id = :cid
          AND c.is_ethics_seminar = FALSE
        GROUP BY mc.name
    """), {"sid": session_id, "cid": curriculum_id}).mappings().all()

    for row in category_credit_rows:
        earned_by_category[row["main_category"]] = int(row["earned_credits"])

    category_audit = []

    for category, required in required_by_category.items():
        earned = earned_by_category.get(category, 0)
        remaining = max(0, required - earned)
        status = "COMPLETED" if remaining == 0 else "INCOMPLETE"

        category_audit.append({
            "main_category": category,
            "required_credits": required,
            "earned_credits": earned,
            "remaining_credits": remaining,
            "status": status
        })

    # --------------------------------------------------
    # 5) Seminar Audit (0 credit, mandatory)
    # --------------------------------------------------
    seminar_total_row = db.execute(text("""
        SELECT COUNT(*) AS total
        FROM courses
        WHERE is_ethics_seminar = TRUE
          AND is_active = TRUE
    """)).mappings().first()

    seminar_total = int(seminar_total_row["total"])

    seminar_completed_row = db.execute(text("""
        SELECT COUNT(DISTINCT c.course_id) AS completed
        FROM session_course_attempts a
        JOIN course_codes cc ON cc.course_code_id = a.course_code_id
        JOIN courses c ON c.course_id = cc.course_id
        WHERE a.session_id = :sid
          AND c.is_ethics_seminar = TRUE
          AND a.grade = 'S'
    """), {"sid": session_id}).mappings().first()

    seminar_completed = int(seminar_completed_row["completed"])
    seminar_remaining = max(0, seminar_total - seminar_completed)
    seminar_status = "COMPLETED" if seminar_remaining == 0 else "INCOMPLETE"

    seminar_audit = {
        "required_total": seminar_total,
        "completed": seminar_completed,
        "remaining": seminar_remaining,
        "status": seminar_status
    }

    # --------------------------------------------------
    # 6) Final Graduation Decision
    # --------------------------------------------------
    graduation_status = "ELIGIBLE_FOR_GRADUATION"

    if total_remaining > 0:
        graduation_status = "NOT_ELIGIBLE"

    for cat in category_audit:
        if cat["status"] == "INCOMPLETE":
            graduation_status = "NOT_ELIGIBLE"
            break

    if seminar_status == "INCOMPLETE":
        graduation_status = "NOT_ELIGIBLE"

    # --------------------------------------------------
    # Final Response
    # --------------------------------------------------
    return {
        "session_id": session_id,
        "curriculum_id": curriculum_id,
        "credit_audit": {
            "earned_credits": earned_credits,
            "required_credits": total_required,
            "remaining_credits": total_remaining,
            "percentage_completed": percentage,
            "status": total_status
        },
        "main_category_audit": category_audit,
        "seminar_audit": seminar_audit,
        "graduation_status": graduation_status
    }