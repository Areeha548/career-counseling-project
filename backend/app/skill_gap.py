"""Calculate transparent, user-specific skill gaps for a catalog career."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .auth import get_current_user
from .database import get_db
from .models import Career, Skill, User, UserSkill, career_skills
from .schemas import CareerSkillGapItem, CareerSkillGapResponse

router = APIRouter(prefix="/api/careers", tags=["skill gap"])

LEVEL_LABELS = {0: "Not familiar", 1: "Beginner", 2: "Intermediate", 3: "Advanced"}
PRIORITY_WEIGHTS = {"high": 3, "medium": 2, "low": 1}
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@router.get("/{career_id}/skill-gap", response_model=CareerSkillGapResponse)
def get_career_skill_gap(
    career_id: int,
    user: User = Depends(get_current_user),
    database: Session = Depends(get_db),
):
    """Compare saved user proficiency against the selected career's requirements."""
    return calculate_skill_gap(career_id, user.id, database)


def calculate_skill_gap(career_id: int, user_id: int, database: Session) -> CareerSkillGapResponse:
    """Shared calculation used by the skill-gap endpoint and roadmap personalization."""
    career = database.scalar(
        select(Career)
        .options(selectinload(Career.skills))
        .where(Career.id == career_id)
    )
    if career is None:
        raise HTTPException(status_code=404, detail="Career not found")

    saved_levels = {
        item.skill_id: item.proficiency_level
        for item in database.scalars(select(UserSkill).where(UserSkill.user_id == user_id)).all()
    }
    requirement_rows = database.execute(
        select(Skill, career_skills.c.priority, career_skills.c.target_level)
        .join(career_skills, career_skills.c.skill_id == Skill.id)
        .where(career_skills.c.career_id == career.id)
    ).all()

    gap_items = []
    readiness_points = 0.0
    possible_points = 0.0
    for skill, priority, target_level in requirement_rows:
        current_level = saved_levels.get(skill.id, 0)
        target_level = int(target_level)
        priority = priority if priority in PRIORITY_WEIGHTS else "medium"
        weight = PRIORITY_WEIGHTS[priority]
        possible_points += weight
        readiness_points += weight * min(current_level, target_level) / target_level
        status = "gap" if current_level == 0 else "strong" if current_level >= target_level else "developing"
        gap_items.append(CareerSkillGapItem(
            skill_id=skill.id,
            name=skill.name,
            category=skill.category,
            proficiency_level=current_level,
            proficiency_label=LEVEL_LABELS[current_level],
            target_level=target_level,
            target_label=LEVEL_LABELS[target_level],
            priority=priority,
            status=status,
        ))

    gap_items.sort(key=lambda item: (PRIORITY_ORDER[item.priority], item.name.casefold()))
    strong_count = sum(item.status == "strong" for item in gap_items)
    developing_count = sum(item.status == "developing" for item in gap_items)
    gap_count = sum(item.status == "gap" for item in gap_items)
    readiness = round(readiness_points / possible_points * 100) if possible_points else 0

    return CareerSkillGapResponse(
        career=career,
        total_required=len(gap_items),
        strong_count=strong_count,
        developing_count=developing_count,
        gap_count=gap_count,
        readiness_percent=readiness,
        readiness_note=(
            "An internal comparison of your self-reported skills with this career profile; "
            "it is not a guarantee of job readiness."
        ),
        skills=gap_items,
    )
