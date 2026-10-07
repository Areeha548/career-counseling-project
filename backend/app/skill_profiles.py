"""Protected endpoints for the current user's catalog-based skill profile."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from .auth import get_current_user
from .database import get_db
from .models import Skill, User, UserSkill
from .schemas import UserSkillProfileResponse, UserSkillProfileUpdate, UserSkillRead

router = APIRouter(prefix="/api/skills/me", tags=["user skills"])


def read_profile(database: Session, user_id: int) -> UserSkillProfileResponse:
    rows = database.scalars(
        select(UserSkill)
        .options(joinedload(UserSkill.skill))
        .where(UserSkill.user_id == user_id)
        .order_by(UserSkill.skill_id)
    ).all()
    skills = [
        UserSkillRead(
            skill_id=row.skill_id,
            name=row.skill.name,
            description=row.skill.description,
            category=row.skill.category,
            proficiency_level=row.proficiency_level,
        )
        for row in rows
    ]
    return UserSkillProfileResponse(skills=skills, count=len(skills))


@router.get("", response_model=UserSkillProfileResponse)
def get_my_skill_profile(
    user: User = Depends(get_current_user),
    database: Session = Depends(get_db),
):
    """Return only the authenticated user's self-reported skills."""
    return read_profile(database, user.id)


@router.put("", response_model=UserSkillProfileResponse)
def save_my_skill_profile(
    profile: UserSkillProfileUpdate,
    user: User = Depends(get_current_user),
    database: Session = Depends(get_db),
):
    """Replace the user's profile, updating levels without duplicate rows."""
    skill_ids = [item.skill_id for item in profile.skills]
    if skill_ids:
        found_ids = set(database.scalars(select(Skill.id).where(Skill.id.in_(skill_ids))).all())
        unknown_ids = sorted(set(skill_ids) - found_ids)
        if unknown_ids:
            raise HTTPException(status_code=422, detail=f"Unknown skill ID(s): {unknown_ids}.")

    existing = database.scalars(select(UserSkill).where(UserSkill.user_id == user.id)).all()
    by_skill_id = {item.skill_id: item for item in existing}
    requested_ids = set(skill_ids)
    for item in profile.skills:
        saved = by_skill_id.get(item.skill_id)
        if saved is None:
            database.add(UserSkill(
                user_id=user.id,
                skill_id=item.skill_id,
                proficiency_level=item.proficiency_level,
            ))
        else:
            saved.proficiency_level = item.proficiency_level

    for saved in existing:
        if saved.skill_id not in requested_ids:
            database.delete(saved)

    database.commit()
    return read_profile(database, user.id)
