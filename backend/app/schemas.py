from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import Literal


class SkillRead(BaseModel):
    id: int
    name: str
    description: str
    category: str

    model_config = ConfigDict(from_attributes=True)


class CareerRead(BaseModel):
    id: int
    name: str
    slug: str
    description: str
    category: str
    difficulty_level: str

    model_config = ConfigDict(from_attributes=True)


class CareerDetail(CareerRead):
    skills: list[SkillRead]


class UserRegister(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    education: str | None = Field(default=None, max_length=160)
    experience_level: str | None = Field(default=None, max_length=80)

    @field_validator("full_name")
    @classmethod
    def clean_full_name(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("Full name must contain at least 2 characters.")
        return value

    @field_validator("education", "experience_level")
    @classmethod
    def clean_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    education: str | None
    experience_level: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class AssessmentOption(BaseModel):
    value: str
    label: str


class AssessmentQuestion(BaseModel):
    id: str
    question_text: str
    category: str
    question_type: str
    options: list[AssessmentOption]
    required: bool


class AssessmentAnswer(BaseModel):
    question_id: str = Field(min_length=1, max_length=40)
    selected_option: str = Field(min_length=1, max_length=80)


class AssessmentSubmit(BaseModel):
    answers: list[AssessmentAnswer] = Field(min_length=1, max_length=100)


class AssessmentSavedAnswer(BaseModel):
    question_id: str
    question_text: str
    category: str
    selected_option: str
    selected_label: str
    created_at: datetime
    updated_at: datetime


class AssessmentResults(BaseModel):
    completed: bool
    answered_count: int
    total_questions: int
    responses: list[AssessmentSavedAnswer]


class AssessmentSubmitResponse(BaseModel):
    message: str
    completed: bool
    answered_count: int
    total_questions: int
    responses: list[AssessmentSavedAnswer]


class CareerRecommendationRead(BaseModel):
    career_id: int
    career_title: str
    description: str
    category: str
    difficulty_level: str
    match_score: float
    ranking: int
    explanation: str
    skills: list[str]
    generated_at: datetime


class RecommendationsResponse(BaseModel):
    completed: bool
    message: str
    generated_at: datetime | None = None
    recommendations: list[CareerRecommendationRead] = Field(default_factory=list)


class UserSkillInput(BaseModel):
    skill_id: int = Field(ge=1)
    proficiency_level: int = Field(ge=0, le=3)


class UserSkillProfileUpdate(BaseModel):
    skills: list[UserSkillInput] = Field(default_factory=list, max_length=120)

    @field_validator("skills")
    @classmethod
    def skill_ids_must_be_unique(cls, skills: list[UserSkillInput]) -> list[UserSkillInput]:
        skill_ids = [item.skill_id for item in skills]
        if len(skill_ids) != len(set(skill_ids)):
            raise ValueError("A skill can only appear once in your profile.")
        return skills


class UserSkillRead(BaseModel):
    skill_id: int
    name: str
    description: str
    category: str
    proficiency_level: int


class UserSkillProfileResponse(BaseModel):
    skills: list[UserSkillRead]
    count: int


class CareerSkillGapItem(BaseModel):
    skill_id: int
    name: str
    category: str
    proficiency_level: int
    proficiency_label: str
    target_level: int
    target_label: str
    priority: Literal["high", "medium", "low"]
    status: Literal["strong", "developing", "gap"]


class CareerSkillGapResponse(BaseModel):
    career: CareerRead
    total_required: int
    strong_count: int
    developing_count: int
    gap_count: int
    readiness_percent: float
    readiness_note: str
    skills: list[CareerSkillGapItem]


class RoadmapCreate(BaseModel):
    career_id: int = Field(ge=1)


class RoadmapTemplateRead(BaseModel):
    career_id: int
    career_name: str
    category: str
    difficulty_level: str
    title: str
    summary: str
    version: int


class RoadmapStepStatusUpdate(BaseModel):
    status: Literal["not_started", "in_progress", "completed"]


class RoadmapStepRead(BaseModel):
    id: int
    template_step_id: int
    order: int
    title: str
    instructions: str
    completion_criteria: str
    skill_id: int | None
    skill_name: str | None
    proficiency_level_at_creation: int | None
    target_level: int | None
    priority: Literal["high", "medium", "low"] | None
    is_optional: bool
    status: Literal["not_started", "in_progress", "completed"]
    started_at: datetime | None
    completed_at: datetime | None
    resource_title: str | None
    resource_url: str | None


class RoadmapPhaseRead(BaseModel):
    id: int
    order: int
    title: str
    objective: str
    description: str
    total_steps: int
    completed_steps: int
    completion_percent: int
    steps: list[RoadmapStepRead]


class UserRoadmapSummary(BaseModel):
    id: int
    career_id: int
    career_name: str
    category: str
    title: str
    template_version: int
    status: Literal["active", "completed"]
    total_steps: int
    completed_steps: int
    completion_percent: int
    current_phase: str | None
    skill_profile_was_empty: bool
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None


class UserRoadmapDetail(UserRoadmapSummary):
    career_description: str
    career_difficulty: str
    summary: str
    phases: list[RoadmapPhaseRead]
    personalization_note: str
