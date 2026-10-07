"""Protected endpoint for personalized career matches."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .auth import get_current_user
from .database import get_db
from .models import User
from .recommendations_service import generate_recommendations
from .schemas import RecommendationsResponse

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("", response_model=RecommendationsResponse)
def get_recommendations(
    user: User = Depends(get_current_user),
    database: Session = Depends(get_db),
):
    """Calculate the current user's ranked career matches from saved answers."""
    recommendations = generate_recommendations(database, user.id)
    generated_at = recommendations[0]["generated_at"] if recommendations else None
    return RecommendationsResponse(
        completed=True,
        message="Career matches are based on your saved assessment answers.",
        generated_at=generated_at,
        recommendations=recommendations,
    )
