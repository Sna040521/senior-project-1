from sqlalchemy import Column, BigInteger, Integer, Text, TIMESTAMP
from sqlalchemy.sql import func
from .db import Base

class AdvisingSession(Base):
    __tablename__ = "advising_sessions"

    session_id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    student_id_number = Column(BigInteger, nullable=False, index=True)
    curriculum_id = Column(Integer, nullable=False, index=True)

    earned_credits = Column(Integer, nullable=False, server_default="0")
    notes = Column(Text, nullable=True)


class SessionCourseAttempt(Base):
    __tablename__ = "session_course_attempts"

    attempt_id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(BigInteger, nullable=False, index=True)

    course_code_id = Column(Integer, nullable=False, index=True)

    grade = Column(Text, nullable=False)
    credits_earned = Column(Integer, nullable=False, server_default="0")
    term = Column(Text, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


class SessionConcentrationSelection(Base):
    __tablename__ = "session_concentration_selection"

    session_id = Column(BigInteger, primary_key=True)
    group_id = Column(Integer, nullable=False)

    selected_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)