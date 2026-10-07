"""Generate and persist a user's latest rule-based career matches."""

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from .assessment_data import ASSESSMENT_QUESTIONS
from .models import AssessmentResponse, Career, CareerRecommendation
from .recommendation_scoring import explanation_for, score_all_careers

RESULT_LIMIT = 10


def generate_recommendations(database: Session, user_id: int) -> list[dict]:
    """Score all catalog careers, persist their latest ranks, and return the top matches."""
    responses = database.scalars(
        select(AssessmentResponse).where(AssessmentResponse.user_id == user_id)
    ).all()
    if len(responses) != len(ASSESSMENT_QUESTIONS):
        raise HTTPException(
            status_code=409,
            detail="Complete the career assessment before viewing recommendations.",
        )

    careers = database.scalars(
        select(Career).options(selectinload(Career.skills)).order_by(Career.id)
    ).all()
    scored = score_all_careers(careers, responses)
    generated_at = datetime.now(timezone.utc)
    existing_rows = database.scalars(
        select(CareerRecommendation).where(CareerRecommendation.user_id == user_id)
    ).all()
    existing_by_career = {item.career_id: item for item in existing_rows}
    current_career_ids = {item["career"].id for item in scored}

    for ranking, item in enumerate(scored, start=1):
        career = item["career"]
        saved = existing_by_career.get(career.id)
        if saved is None:
            saved = CareerRecommendation(user_id=user_id, career_id=career.id)
            database.add(saved)
        saved.match_score = item["match_score"]
        saved.ranking = ranking
        saved.generated_at = generated_at

    stale_ids = [row.id for row in existing_rows if row.career_id not in current_career_ids]
    if stale_ids:
        database.execute(delete(CareerRecommendation).where(CareerRecommendation.id.in_(stale_ids)))
    database.commit()

    return [
        {
            "career_id": item["career"].id,
            "career_title": item["career"].name,
            "description": item["career"].description,
            "category": item["career"].category,
            "difficulty_level": item["career"].difficulty_level,
            "match_score": item["match_score"],
            "ranking": ranking,
            "explanation": explanation_for(item["reasons"]),
            "skills": [skill.name for skill in item["career"].skills],
            "generated_at": generated_at,
        }
        for ranking, item in enumerate(scored[:RESULT_LIMIT], start=1)
    ]
