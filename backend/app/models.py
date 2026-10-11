from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String, Table, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

career_skills = Table(
    "career_skills",
    Base.metadata,
    Column("career_id", ForeignKey("careers.id"), primary_key=True),
    Column("skill_id", ForeignKey("skills.id"), primary_key=True),
    Column("priority", String(12), nullable=False, server_default=text("'medium'")),
    Column("target_level", Integer, nullable=False, server_default=text("2")),
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
    user_profiles: Mapped[list["UserSkill"]] = relationship(
        back_populates="skill",
        cascade="all, delete-orphan",
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
    skill_profiles: Mapped[list["UserSkill"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    roadmaps: Mapped[list["UserRoadmap"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class UserSkill(Base):
    """A user's self-reported proficiency for one catalog skill."""

    __tablename__ = "user_skills"
    __table_args__ = (
        UniqueConstraint("user_id", "skill_id", name="uq_user_skill_profile"),
        CheckConstraint("proficiency_level >= 0 AND proficiency_level <= 3", name="ck_user_skill_level"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    proficiency_level: Mapped[int] = mapped_column(Integer, nullable=False)

    user: Mapped["User"] = relationship(back_populates="skill_profiles")
    skill: Mapped[Skill] = relationship(back_populates="user_profiles")


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


class RoadmapTemplate(Base):
    """A versioned, reusable learning plan for one catalog career."""

    __tablename__ = "roadmap_templates"
    __table_args__ = (
        UniqueConstraint("career_id", "version", name="uq_roadmap_template_career_version"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    career_id: Mapped[int] = mapped_column(ForeignKey("careers.id", ondelete="CASCADE"), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False,
    )

    career: Mapped[Career] = relationship()
    phases: Mapped[list["RoadmapPhaseTemplate"]] = relationship(
        back_populates="template", cascade="all, delete-orphan", order_by="RoadmapPhaseTemplate.phase_order",
    )
    roadmaps: Mapped[list["UserRoadmap"]] = relationship(back_populates="template")


class RoadmapPhaseTemplate(Base):
    """An ordered milestone in a career roadmap template."""

    __tablename__ = "roadmap_phase_templates"
    __table_args__ = (UniqueConstraint("template_id", "phase_order", name="uq_roadmap_phase_order"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("roadmap_templates.id", ondelete="CASCADE"), nullable=False, index=True)
    phase_order: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    objective: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    template: Mapped[RoadmapTemplate] = relationship(back_populates="phases")
    steps: Mapped[list["RoadmapStepTemplate"]] = relationship(
        back_populates="phase", cascade="all, delete-orphan", order_by="RoadmapStepTemplate.step_order",
    )


class RoadmapStepTemplate(Base):
    """Curated instructions and measurable criteria for one roadmap step."""

    __tablename__ = "roadmap_step_templates"
    __table_args__ = (UniqueConstraint("phase_id", "step_order", name="uq_roadmap_step_order"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    phase_id: Mapped[int] = mapped_column(ForeignKey("roadmap_phase_templates.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id: Mapped[int | None] = mapped_column(ForeignKey("skills.id", ondelete="SET NULL"), nullable=True, index=True)
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    completion_criteria: Mapped[str] = mapped_column(Text, nullable=False)
    resource_title: Mapped[str | None] = mapped_column(String(180), nullable=True)
    resource_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    resource_search: Mapped[str | None] = mapped_column(String(300), nullable=True)
    prerequisites: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=60, server_default="60")

    phase: Mapped[RoadmapPhaseTemplate] = relationship(back_populates="steps")
    skill: Mapped[Skill | None] = relationship()


class UserRoadmap(Base):
    """One user's independent, resumable roadmap for a selected career."""

    __tablename__ = "user_roadmaps"
    __table_args__ = (
        UniqueConstraint("user_id", "career_id", name="uq_user_roadmap_career"),
        CheckConstraint("status IN ('active', 'completed')", name="ck_user_roadmap_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    career_id: Mapped[int] = mapped_column(ForeignKey("careers.id", ondelete="CASCADE"), nullable=False, index=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("roadmap_templates.id", ondelete="RESTRICT"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active", server_default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc), nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    skill_profile_was_empty: Mapped[bool] = mapped_column(default=False, nullable=False)

    user: Mapped[User] = relationship(back_populates="roadmaps")
    career: Mapped[Career] = relationship()
    template: Mapped[RoadmapTemplate] = relationship(back_populates="roadmaps")
    step_progress: Mapped[list["UserRoadmapStepProgress"]] = relationship(
        back_populates="roadmap", cascade="all, delete-orphan",
    )


class UserRoadmapStepProgress(Base):
    """Progress for a template step, isolated to one user's roadmap."""

    __tablename__ = "user_roadmap_step_progress"
    __table_args__ = (
        UniqueConstraint("roadmap_id", "step_template_id", name="uq_user_roadmap_step"),
        CheckConstraint("status IN ('not_started', 'in_progress', 'completed')", name="ck_user_roadmap_step_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    roadmap_id: Mapped[int] = mapped_column(ForeignKey("user_roadmaps.id", ondelete="CASCADE"), nullable=False, index=True)
    step_template_id: Mapped[int] = mapped_column(ForeignKey("roadmap_step_templates.id", ondelete="RESTRICT"), nullable=False, index=True)
    personalized_order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_optional: Mapped[bool] = mapped_column(default=False, nullable=False)
    proficiency_level_at_creation: Mapped[int | None] = mapped_column(Integer, nullable=True)
    priority_at_creation: Mapped[str | None] = mapped_column(String(12), nullable=True)
    target_level_at_creation: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_minutes_at_creation: Mapped[int] = mapped_column(Integer, nullable=False, default=60, server_default="60")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="not_started", server_default="not_started")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    roadmap: Mapped[UserRoadmap] = relationship(back_populates="step_progress")
    step_template: Mapped[RoadmapStepTemplate] = relationship()
