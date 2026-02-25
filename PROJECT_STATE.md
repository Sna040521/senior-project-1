Project: Curriculum Advisor Senior Project
Status: Backend core engine stable

Completed:
- Advising session creation
- Transcript upload
- Concentration selection
- Grade validation with curriculum min grade
- Prerequisite logic
- Credit requirement logic
- Major elective grouping (explicit + range)
- Elective progress tracking
- Priority state logic
- Soft enforcement next semester planner
- max_credits configurable (default 18)

Current Curriculum Implemented:
- BSCS 653 (curriculum_id = 1)

Next Goals:
- Possibly graduation audit endpoint
- Planner refinement
- Frontend integration
- Extend to other 9 curriculums

Important:
- Backend working with Swagger
- Endpoint: GET /advising-session/{session_id}/recommendations
- max_credits query param supported

