from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

career_skills = Table(
    "career_skills",
    Base.metadata,
    Column("career_id", ForeignKey("careers.id"), primary_key=True),
    Column("skill_id", ForeignKey("skills.id"), primary_key=True),
)


class DatabaseCheck(Base):
    """Small table used to verify database connectivity."""

    __tablename__ = "database_checks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)


class Career(Base):
    """A career path that a user can explore."""

    __tablename__ = "careers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(140), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    difficulty_level: Mapped[str] = mapped_column(String(40), nullable=False)

    skills: Mapped[list["Skill"]] = relationship(
        secondary=career_skills,
        back_populates="careers",
    )


class Skill(Base):
    """A skill that can be useful in several careers."""

    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)

    careers: Mapped[list[Career]] = relationship(
        secondary=career_skills,
        back_populates="skills",
    )


class User(Base):
    """An account that can authenticate to the Career Mentor API."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    education: Mapped[str | None] = mapped_column(String(160), nullable=True)
    experience_level: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    assessment_responses: Mapped[list["AssessmentResponse"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    recommendations: Mapped[list["CareerRecommendation"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class AssessmentResponse(Base):
    """One saved answer for a user's career assessment."""

    __tablename__ = "assessment_responses"
    __table_args__ = (UniqueConstraint("user_id", "question_id", name="uq_assessment_user_question"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id: Mapped[str] = mapped_column(String(40), nullable=False)
    selected_option: Mapped[str] = mapped_column(String(80), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped[User] = relationship(back_populates="assessment_responses")


class CareerRecommendation(Base):
    """Latest calculated match for one user's career catalog entry."""

    __tablename__ = "career_recommendations"
    __table_args__ = (UniqueConstraint("user_id", "career_id", name="uq_recommendation_user_career"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    career_id: Mapped[int] = mapped_column(ForeignKey("careers.id", ondelete="CASCADE"), nullable=False, index=True)
    match_score: Mapped[float] = mapped_column(nullable=False)
    ranking: Mapped[int] = mapped_column(nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped[User] = relationship(back_populates="recommendations")
    career: Mapped[Career] = relationship()
