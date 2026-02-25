# app/services/grading.py

GRADE_RANK = {
    "A": 10, "A-": 9,
    "B+": 8, "B": 7, "B-": 6,
    "C+": 5, "C": 4, "C-": 3,
    "D+": 2, "D": 1,
    "F": 0,
}

SPECIAL_PASS = {"S", "TR"}   # TR always pass
SPECIAL_FAIL = {"W", "IP"}   # Withdraw + In Progress = not passed


def normalize_grade(g: str) -> str:
    return g.strip().upper()


def is_passing(student_grade: str, required_grade: str) -> bool:
    sg = normalize_grade(student_grade)
    rg = normalize_grade(required_grade)

    # Special pass cases
    if sg in SPECIAL_PASS:
        return True

    # Special fail cases
    if sg in SPECIAL_FAIL:
        return False

    # If unknown grade
    if sg not in GRADE_RANK:
        return False

    # If required grade not defined, default to D
    if rg not in GRADE_RANK:
        rg = "D"

    return GRADE_RANK[sg] >= GRADE_RANK[rg]