"""Authenticated endpoints for the user's career assessment."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .assessment_data import ASSESSMENT_QUESTIONS, QUESTION_BY_ID
from .auth import get_current_user
from .database import get_db
from .models import AssessmentResponse, User
from .recommendations_service import generate_recommendations
from .schemas import (
    AssessmentQuestion,
    AssessmentResults,
    AssessmentSavedAnswer,
    AssessmentSubmit,
    AssessmentSubmitResponse,
)

router = APIRouter(prefix="/api/assessment", tags=["assessment"])


def response_for(saved: AssessmentResponse) -> AssessmentSavedAnswer:
    question = QUESTION_BY_ID[saved.question_id]
    option = next(item for item in question["options"] if item["value"] == saved.selected_option)
    return AssessmentSavedAnswer(
        question_id=saved.question_id,
        question_text=question["question_text"],
        category=question["category"],
        selected_option=saved.selected_option,
        selected_label=option["label"],
        created_at=saved.created_at,
        updated_at=saved.updated_at,
    )


@router.get("/questions", response_model=list[AssessmentQuestion])
def get_assessment_questions(user: User = Depends(get_current_user)):
    """Return the question catalog to an authenticated user."""
    return ASSESSMENT_QUESTIONS


@router.post("/submit", response_model=AssessmentSubmitResponse)
def submit_assessment(
    payload: AssessmentSubmit,
    user: User = Depends(get_current_user),
    database: Session = Depends(get_db),
):
    """Validate and save the user's complete set of assessment answers."""
    answers_by_id = {}
    for answer in payload.answers:
        question = QUESTION_BY_ID.get(answer.question_id)
        if question is None:
            raise HTTPException(status_code=422, detail=f"Unknown question ID: {answer.question_id}.")
        if answer.question_id in answers_by_id:
            raise HTTPException(status_code=422, detail=f"Question {answer.question_id} was answered more than once.")
        allowed_values = {option["value"] for option in question["options"]}
        if answer.selected_option not in allowed_values:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid option for question {answer.question_id}.",
            )
        answers_by_id[answer.question_id] = answer.selected_option

    missing = [
        question["id"]
        for question in ASSESSMENT_QUESTIONS
        if question["required"] and question["id"] not in answers_by_id
    ]
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Please answer all required questions. Missing: {', '.join(missing)}.",
        )

    existing = database.scalars(
        select(AssessmentResponse).where(
            AssessmentResponse.user_id == user.id,
            AssessmentResponse.question_id.in_(answers_by_id),
        )
    ).all()
    existing_by_question = {item.question_id: item for item in existing}

    for question_id, selected_option in answers_by_id.items():
        saved = existing_by_question.get(question_id)
        if saved is None:
            database.add(
                AssessmentResponse(
                    user_id=user.id,
                    question_id=question_id,
                    selected_option=selected_option,
                )
            )
        else:
            saved.selected_option = selected_option

    database.commit()
    saved_answers = database.scalars(
        select(AssessmentResponse)
        .where(AssessmentResponse.user_id == user.id)
        .order_by(AssessmentResponse.question_id)
    ).all()
    responses = [response_for(saved) for saved in saved_answers]
    completed = len(responses) == len(ASSESSMENT_QUESTIONS)
    if completed:
        # Retaking the assessment immediately refreshes the user's stored matches.
        generate_recommendations(database, user.id)
    return AssessmentSubmitResponse(
        message="Your assessment has been saved.",
        completed=completed,
        answered_count=len(responses),
        total_questions=len(ASSESSMENT_QUESTIONS),
        responses=responses,
    )


@router.get("/my-results", response_model=AssessmentResults)
def get_my_assessment_results(
    user: User = Depends(get_current_user),
    database: Session = Depends(get_db),
):
    """Return only the signed-in user's saved answers."""
    saved_answers = database.scalars(
        select(AssessmentResponse)
        .where(AssessmentResponse.user_id == user.id)
        .order_by(AssessmentResponse.question_id)
    ).all()
    responses = [response_for(saved) for saved in saved_answers]
    return AssessmentResults(
        completed=len(responses) == len(ASSESSMENT_QUESTIONS),
        answered_count=len(responses),
        total_questions=len(ASSESSMENT_QUESTIONS),
        responses=responses,
    )
