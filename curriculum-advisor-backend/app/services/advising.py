# app/services/advising.py

from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import text
import re
from typing import Optional, Dict, Any, List

from .grading import is_passing


# ============================================================
# Next semester plan (soft enforcement)
# ============================================================

def build_next_semester_plan(
    eligible_by_subcat: dict,
    elective_priority: Optional[str],
    max_credits: int = 18
) -> dict:
    """
    Soft enforcement planner:
    - Always show a plan (even if electives not selected)
    - Uses priority to pick elective buckets earlier or later
    - Never exceeds max_credits
    """

    plan: List[dict] = []
    total_credits = 0
    picked_codes = set()
    notes: List[str] = []

    def add_from(items: List[dict], source: str):
        nonlocal total_credits
        for c in items:
            code = c.get("course_code")
            credits = int(c.get("credits", 0))

            if not code or code in picked_codes:
                continue
            if total_credits + credits > max_credits:
                continue

            plan.append({
                "course_code": code,
                "course_name": c.get("course_name"),
                "credits": credits,
                "source": source
            })
            picked_codes.add(code)
            total_credits += credits

            if total_credits >= max_credits:
                break

    # 1) Other Specialized Courses first
    other_spec = eligible_by_subcat.get("Other Specialized Courses")
    if isinstance(other_spec, dict):
        add_from(other_spec.get("eligible", []), "Other Specialized Courses")

    if total_credits >= max_credits:
        return {
            "max_credits": max_credits,
            "total_credits": total_credits,
            "recommended_courses": plan,
            "notes": notes
        }

    # 2) Major Electives (structure differs by selected / not selected)
    electives = eligible_by_subcat.get("Major Electives")

    if isinstance(electives, dict):

        # Case A: not selected
        if "message" in electives:
            notes.append(electives.get("message", "Concentration not selected."))

            open_pool = electives.get("open_pool", {})
            if isinstance(open_pool, dict):
                add_from(open_pool.get("eligible", []), "Major Electives (Open Pool)")

        # Case B: selected
        else:
            chosen = electives.get("chosen_track", {})
            other = electives.get("other_tracks", {})
            open_pool = electives.get("open_pool", {})

            chosen_list = chosen.get("eligible", []) if isinstance(chosen, dict) else []
            other_list = other.get("eligible", []) if isinstance(other, dict) else []
            open_list = open_pool.get("eligible", []) if isinstance(open_pool, dict) else []

            # Priority ordering (soft enforcement)
            if elective_priority == "FOCUS_ON_CHOSEN_TRACK":
                add_from(chosen_list, "Major Electives (Chosen Track)")
                add_from(open_list, "Major Electives (Open Pool)")
                add_from(other_list, "Major Electives (Other Tracks)")
            elif elective_priority == "FREE_CHOICE":
                add_from(open_list, "Major Electives (Open Pool)")
                add_from(chosen_list, "Major Electives (Chosen Track)")
                add_from(other_list, "Major Electives (Other Tracks)")
            else:
                # default safe order
                add_from(chosen_list, "Major Electives (Chosen Track)")
                add_from(open_list, "Major Electives (Open Pool)")
                add_from(other_list, "Major Electives (Other Tracks)")

    if total_credits < max_credits:
        notes.append(f"Plan underfilled: {total_credits}/{max_credits} credits (not enough eligible courses yet).")

    return {
        "max_credits": max_credits,
        "total_credits": total_credits,
        "recommended_courses": plan,
        "notes": notes
    }
def get_next_ethics_seminar(session_id: int, db: Session) -> Optional[dict]:
    """
    Returns the next required Professional Ethics Seminar (0 credit)
    that is NOT yet completed with grade 'S'.

    Rule:
    - Only grade 'S' counts as completed.
    - 'W' and 'F' are NOT completed.
    """
    # All seminar course codes in order (BG14030 ..)
    seminars = db.execute(text("""
        SELECT
            cc.course_code,
            c.course_name,
            c.credits
        FROM courses c
        JOIN course_codes cc ON cc.course_id = c.course_id
        WHERE c.is_ethics_seminar = TRUE
          AND c.is_active = TRUE
          AND cc.is_active = TRUE
        ORDER BY cc.course_code
    """)).mappings().all()

    if not seminars:
        return None

    # Find first seminar NOT completed with grade 'S'
    for s in seminars:
        completed = db.execute(text("""
            SELECT 1
            FROM session_course_attempts a
            JOIN course_codes cc ON cc.course_code_id = a.course_code_id
            JOIN courses c ON c.course_id = cc.course_id
            WHERE a.session_id = :sid
              AND c.is_ethics_seminar = TRUE
              AND cc.course_code = :code
              AND a.grade IN ('S', 'IP')
            LIMIT 1
        """), {"sid": session_id, "code": s["course_code"]}).scalar()

        if not completed:
            return {
                "course_code": s["course_code"],
                "course_name": s["course_name"],
                "credits": int(s["credits"]),  # should be 0
                "source": "Professional Ethics Seminar (Required)"
            }

    # All completed
    return None

# ============================================================
# Main recommendation builder
# ============================================================

def build_recommendations(
    session_id: int,
    db: Session,
    max_credits: int = 18,
    offered_courses: Optional[List[str]] = None
) -> Dict[str, Any]:
    # load session
    s = db.execute(
        text("SELECT session_id, curriculum_id FROM advising_sessions WHERE session_id = :sid"),
        {"sid": session_id}
    ).mappings().first()

    if not s:
        return {"error": "Session not found"}

    curriculum_id = int(s["curriculum_id"])

    # attempts + required grade
    attempts = db.execute(text("""
        SELECT
            a.attempt_id,
            a.grade,
            a.course_code_id,
            cc.course_code,
            c.course_id,
            c.credits,
            COALESCE(mg.min_required_grade::text, 'D') AS required_grade
        FROM session_course_attempts a
        JOIN course_codes cc ON cc.course_code_id = a.course_code_id
        JOIN courses c ON c.course_id = cc.course_id
        LEFT JOIN curriculum_course_min_grades mg
            ON mg.curriculum_id = :cid AND mg.course_id = c.course_id
        WHERE a.session_id = :sid
        ORDER BY a.attempt_id
    """), {"sid": session_id, "cid": curriculum_id}).mappings().all()

    passed_course_ids = set()
    passed_codes = set()
    failed_codes = set()
    passed_course_code_ids = set()
    in_progress_course_ids = set()
    in_progress_course_code_ids = set()

    for row in attempts:
        grade = row["grade"].strip().upper()

        # --- IP handling ---
        if grade == "IP":
            in_progress_course_ids.add(int(row["course_id"]))
            in_progress_course_code_ids.add(int(row["course_code_id"]))
            continue

        # --- Normal pass/fail handling ---
        ok = is_passing(row["grade"], row["required_grade"])

        if ok:
            passed_course_ids.add(int(row["course_id"]))
            passed_codes.add(row["course_code"])
            passed_course_code_ids.add(int(row["course_code_id"]))
        else:
            failed_codes.add(row["course_code"])

    # earned credits = sum credits of unique passed courses
    earned_row = db.execute(text("""
        SELECT COALESCE(SUM(a.credits_earned), 0) AS earned_credits
        FROM session_course_attempts a
        WHERE a.session_id = :sid
            AND a.credits_earned > 0
    """), {"sid": session_id}).mappings().first()

    earned_credits = int(earned_row["earned_credits"])
    
    # --------------------------------------------------------
    # Load main category required credits (GE, FE)
    # --------------------------------------------------------
    required_by_category = {}

    required_rows = db.execute(text("""
        SELECT 
            mc.main_category_id,
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
            COALESCE(SUM(a.credits_earned), 0) AS earned_credits 
        FROM session_course_attempts a
        JOIN course_codes cc ON cc.course_code_id = a.course_code_id
        JOIN courses c ON c.course_id = cc.course_id
        JOIN subcategory_course_codes sc ON sc.course_code_id = cc.course_code_id
        JOIN curriculum_subcategories sub ON sub.subcategory_id = sc.subcategory_id
        JOIN main_categories mc ON mc.main_category_id = sub.main_category_id
        WHERE a.session_id = :sid
          AND sub.curriculum_id = :cid
          AND a.credits_earned > 0
        GROUP BY mc.name
    """), {"sid": session_id, "cid": curriculum_id}).mappings().all()

    for row in category_credit_rows:
        earned_by_category[row["main_category"]] = int(row["earned_credits"])

    ge_remaining = max(
        0,
        required_by_category.get("General Education", 0)
        - earned_by_category.get("General Education", 0)
    )

    fe_remaining = max(
        0,
        required_by_category.get("Free Electives", 0)
        - earned_by_category.get("Free Electives", 0)
    )

    # Major elective subcategory (if exists)
    elective_subcat = db.execute(text("""
        SELECT subcategory_id, name
        FROM curriculum_subcategories
        WHERE curriculum_id = :cid AND name ILIKE '%Major Elective%'
        LIMIT 1
    """), {"cid": curriculum_id}).mappings().first()
    elective_subcategory_id = int(elective_subcat["subcategory_id"]) if elective_subcat else None

    elective_rules = db.execute(text("""
        SELECT min_from_chosen_group, min_from_all_groups
        FROM major_elective_rules
        WHERE curriculum_id = :cid
        LIMIT 1
    """), {"cid": curriculum_id}).mappings().first()

    chosen_group_id = db.execute(text("""
        SELECT group_id
        FROM session_concentration_selection
        WHERE session_id = :sid
        LIMIT 1
    """), {"sid": session_id}).scalar()
    chosen_group_id = int(chosen_group_id) if chosen_group_id else None

    def resolve_elective_group(course_code_id: int, course_code: str) -> Optional[int]:
        # explicit mapping
        g = db.execute(text("""
            SELECT group_id
            FROM major_elective_group_course_codes
            WHERE course_code_id = :ccid
            LIMIT 1
        """), {"ccid": course_code_id}).scalar()
        if g:
            return int(g)

        # range mapping
        if not elective_subcategory_id:
            return None

        m = re.match(r"^([A-Za-z]+)(\d+)$", course_code.strip())
        if not m:
            return None

        prefix = m.group(1).upper()
        num = int(m.group(2))

        g2 = db.execute(text("""
            SELECT group_id
            FROM course_code_ranges
            WHERE subcategory_id = :subid
              AND UPPER(prefix) = :prefix
              AND :num BETWEEN number_start AND number_end
            LIMIT 1
        """), {"subid": elective_subcategory_id, "prefix": prefix, "num": num}).scalar()

        return int(g2) if g2 else None

    # --------------------------------------------------------
    # Elective progress (count courses)
    # --------------------------------------------------------
    elective_progress = None
    passed_elective_course_code_ids = set()

    if elective_rules and elective_subcategory_id:
        passed_attempt_rows = db.execute(text("""
            SELECT DISTINCT a.course_code_id, cc.course_code
            FROM session_course_attempts a
            JOIN course_codes cc ON cc.course_code_id = a.course_code_id
            JOIN subcategory_course_codes sc ON sc.course_code_id = a.course_code_id
            WHERE a.session_id = :sid
              AND sc.subcategory_id = :subid
        """), {"sid": session_id, "subid": elective_subcategory_id}).mappings().all()

        chosen_done = 0
        any_done = 0

        for r in passed_attempt_rows:
            ccid = int(r["course_code_id"])
            code = r["course_code"]

            if ccid not in passed_course_code_ids:
                continue

            g = resolve_elective_group(ccid, code)
            if g is None:
                continue

            passed_elective_course_code_ids.add(ccid)
            any_done += 1
            if chosen_group_id and g == chosen_group_id:
                chosen_done += 1

        elective_progress = {
            "track_status": "SELECTED" if chosen_group_id else "NOT_SELECTED",
            "chosen_group_id": chosen_group_id,
            "min_from_chosen_group": int(elective_rules["min_from_chosen_group"]),
            "min_from_all_groups": int(elective_rules["min_from_all_groups"]),
            "chosen_group_completed": chosen_done,
            "all_groups_completed": any_done,
            "chosen_group_remaining": max(0, int(elective_rules["min_from_chosen_group"]) - chosen_done),
            "all_groups_remaining": max(0, int(elective_rules["min_from_all_groups"]) - any_done),
        }

    # Determine elective priority state
    priority_state = None
    if elective_progress:
        if not chosen_group_id:
            priority_state = "SELECT_CONCENTRATION_FIRST"
        elif elective_progress["all_groups_remaining"] == 0:
            priority_state = "ELECTIVE_REQUIREMENT_COMPLETED"
        elif elective_progress["chosen_group_remaining"] > 0:
            priority_state = "FOCUS_ON_CHOSEN_TRACK"
        else:
            priority_state = "FREE_CHOICE"

    # --------------------------------------------------------
    # Candidates (specialized only)
    # --------------------------------------------------------
    candidates = db.execute(text("""
        SELECT
            cc.course_code,
            cc.course_code_id,
            c.course_id,
            c.course_name,
            c.credits,
            sub.subcategory_id,
            sub.name AS subcategory_name,
            COALESCE(cr.min_earned_credits, 0) AS min_credits_required
        FROM curriculum_subcategories sub
        JOIN subcategory_course_codes sc ON sc.subcategory_id = sub.subcategory_id
        JOIN course_codes cc ON cc.course_code_id = sc.course_code_id
        JOIN courses c ON c.course_id = cc.course_id
        LEFT JOIN curriculum_course_credit_requirements cr
            ON cr.curriculum_id = :cid AND cr.course_id = c.course_id
        WHERE sub.curriculum_id = :cid
          AND sub.main_category_id = 2
        ORDER BY sub.display_order, cc.course_code
    """), {"cid": curriculum_id}).mappings().all()

    # prereq map
    prereqs = db.execute(text("""
        SELECT course_id, prerequisite_course_id
        FROM course_prerequisites
    """)).mappings().all()

    prereq_map: Dict[int, List[int]] = {}
    for p in prereqs:
        prereq_map.setdefault(int(p["course_id"]), []).append(int(p["prerequisite_course_id"]))

    # --------------------------------------------------------
    # Eligible output buckets
    # --------------------------------------------------------
    eligible_by_subcat: Dict[str, Any] = {}

    chosen_track_list = []
    other_track_list = []
    open_pool_list = []

    chosen_track_blocked_prereq = []
    chosen_track_blocked_credit = []
    chosen_track_completed = []

    other_track_blocked_prereq = []
    other_track_blocked_credit = []
    other_track_completed = []

    open_pool_blocked_prereq = []
    open_pool_blocked_credit = []
    open_pool_completed = []

    normal_specialized = {
        "eligible": [],
        "blocked_by_prerequisite": [],
        "blocked_by_credit_requirement": [],
        "already_completed": []
    }

    for c in candidates:
        course_id = int(c["course_id"])
        subcat_id = int(c["subcategory_id"])
        course_code_id = int(c["course_code_id"])
        course_code = c["course_code"]

        item = {
            "course_code": course_code,
            "course_name": c["course_name"],
            "credits": int(c["credits"]),
        }

        # determine blocking reason
        if course_id in passed_course_ids or course_id in in_progress_course_ids:
            block_reason = "completed"
        elif earned_credits < int(c["min_credits_required"]):
            block_reason = "credit"
        else:
            needed = prereq_map.get(course_id, [])
            if any(req not in passed_course_ids for req in needed):
                block_reason = "prereq"
            else:
                block_reason = "eligible"

        # non-elective -> normal specialized
        if elective_subcategory_id is None or subcat_id != elective_subcategory_id:
            if block_reason == "eligible":
                normal_specialized["eligible"].append(item)
            elif block_reason == "prereq":
                normal_specialized["blocked_by_prerequisite"].append(item)
            elif block_reason == "credit":
                normal_specialized["blocked_by_credit_requirement"].append(item)
            elif block_reason == "completed":
                normal_specialized["already_completed"].append(item)
            continue

        # elective course -> resolve group
        group = resolve_elective_group(course_code_id, course_code)

        # Group 3 = open pool
        if group == 3:
            if block_reason == "eligible":
                open_pool_list.append(item)
            elif block_reason == "prereq":
                open_pool_blocked_prereq.append(item)
            elif block_reason == "credit":
                open_pool_blocked_credit.append(item)
            elif block_reason == "completed":
                open_pool_completed.append(item)

        # chosen track
        elif chosen_group_id and group == chosen_group_id:
            if block_reason == "eligible":
                chosen_track_list.append(item)
            elif block_reason == "prereq":
                chosen_track_blocked_prereq.append(item)
            elif block_reason == "credit":
                chosen_track_blocked_credit.append(item)
            elif block_reason == "completed":
                chosen_track_completed.append(item)

        # other tracks
        else:
            if block_reason == "eligible":
                other_track_list.append(item)
            elif block_reason == "prereq":
                other_track_blocked_prereq.append(item)
            elif block_reason == "credit":
                other_track_blocked_credit.append(item)
            elif block_reason == "completed":
                other_track_completed.append(item)

    # Assemble final structure
    if (
        normal_specialized["eligible"]
        or normal_specialized["blocked_by_prerequisite"]
        or normal_specialized["blocked_by_credit_requirement"]
        or normal_specialized["already_completed"]
    ):
        eligible_by_subcat["Other Specialized Courses"] = normal_specialized

    if elective_subcategory_id:
        if not chosen_group_id:
            eligible_by_subcat["Major Electives"] = {
                "message": "Please select a concentration to see track-specific recommendations.",
                "open_pool": {
                    "eligible": open_pool_list,
                    "blocked_by_prerequisite": open_pool_blocked_prereq,
                    "blocked_by_credit_requirement": open_pool_blocked_credit,
                    "already_completed": open_pool_completed,
                }
            }
        else:
            eligible_by_subcat["Major Electives"] = {
                "chosen_track": {
                    "eligible": chosen_track_list,
                    "blocked_by_prerequisite": chosen_track_blocked_prereq,
                    "blocked_by_credit_requirement": chosen_track_blocked_credit,
                    "already_completed": chosen_track_completed,
                },
                "other_tracks": {
                    "eligible": other_track_list,
                    "blocked_by_prerequisite": other_track_blocked_prereq,
                    "blocked_by_credit_requirement": other_track_blocked_credit,
                    "already_completed": other_track_completed,
                },
                "open_pool": {
                    "eligible": open_pool_list,
                    "blocked_by_prerequisite": open_pool_blocked_prereq,
                    "blocked_by_credit_requirement": open_pool_blocked_credit,
                    "already_completed": open_pool_completed,
                }
            }
    # --------------------------------------------------------
    # Filter by offered courses (if provided)
    # --------------------------------------------------------
    if offered_courses:
        offered_set = set(code.strip().upper() for code in offered_courses)

        def filter_list(course_list):
            return [
                c for c in course_list
                if c["course_code"].upper() in offered_set
            ]

        for key, value in eligible_by_subcat.items():

            if key == "Other Specialized Courses":
                for bucket in value:
                    value[bucket] = filter_list(value[bucket])

            elif key == "Major Electives":
                for subkey in value:
                    if isinstance(value[subkey], dict):
                        for bucket in value[subkey]:
                            if isinstance(value[subkey][bucket], list):
                                value[subkey][bucket] = filter_list(value[subkey][bucket])

    # Next semester plan (soft enforcement)
    next_semester_plan = build_next_semester_plan(
        eligible_by_subcat=eligible_by_subcat,
        elective_priority=priority_state,
        max_credits=max_credits
    )

    # --------------------------------------------------------
    # Add Professional Ethics Seminar (0 credit, mandatory)
    # --------------------------------------------------------
    next_seminar = get_next_ethics_seminar(session_id=session_id, db=db)
    if next_seminar:
        # Always include it even if max credits already reached (0 credit anyway)
        next_semester_plan["recommended_courses"].append(next_seminar)
        # total_credits unchanged because seminar credits are 0

    # --------------------------------------------------------
    # Add General Education placeholder (if remaining)
    # --------------------------------------------------------
    if ge_remaining > 0:
        next_semester_plan["recommended_courses"].append({
            "course_code": "GE",
            "course_name": "General Education (Select 1 Course)",
            "credits": min(ge_remaining, 3),  # Suggest up to 3 credits per semester
            "source": "General Education"
        })

    # --------------------------------------------------------
    # Add Free Elective placeholder (if remaining)
    # --------------------------------------------------------
    if fe_remaining > 0:
        next_semester_plan["recommended_courses"].append({
            "course_code": "FE",
            "course_name": "Free Elective (Select 1 Course)",
            "credits": min(fe_remaining, 3),
            "source": "Free Elective"
        })

    return {
        "session_id": session_id,
        "curriculum_id": curriculum_id,
        "earned_credits": earned_credits,
        "passed_course_codes": sorted(passed_codes),
        "failed_course_codes": sorted(failed_codes),
        "elective_progress": elective_progress,
        "elective_priority": priority_state,
        "eligible_specialized_by_subcategory": eligible_by_subcat,
        "next_semester_plan": next_semester_plan
    }