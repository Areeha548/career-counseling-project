"""Protected API for creating and tracking personalized career roadmaps."""

from datetime import datetime, timezone
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload

from .auth import get_current_user
from .database import get_db
from .models import (
    Career,
    RoadmapStepTemplate,
    RoadmapTemplate,
    User,
    UserRoadmap,
    UserRoadmapStepProgress,
    UserSkill,
)
from .schemas import (
    RoadmapCreate,
    RoadmapPhaseRead,
    RoadmapStepRead,
    RoadmapStepStatusUpdate,
    RoadmapTemplateRead,
    UserRoadmapDetail,
    UserRoadmapSummary,
)
from .skill_gap import calculate_skill_gap

router = APIRouter(prefix="/api/roadmaps", tags=["roadmaps"])
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def _roadmap_query():
    return select(UserRoadmap).options(
        joinedload(UserRoadmap.career),
        joinedload(UserRoadmap.template),
        selectinload(UserRoadmap.step_progress)
        .joinedload(UserRoadmapStepProgress.step_template)
        .joinedload(RoadmapStepTemplate.skill),
        selectinload(UserRoadmap.step_progress)
        .joinedload(UserRoadmapStepProgress.step_template)
        .joinedload(RoadmapStepTemplate.phase),
    )


def _progress_counts(roadmap: UserRoadmap) -> tuple[int, int, int, str | None]:
    required = [row for row in roadmap.step_progress if not row.is_optional]
    completed = sum(row.status == "completed" for row in required)
    total = len(required)
    percent = round(completed / total * 100) if total else 0
    ordered_phases = sorted(roadmap.template.phases, key=lambda phase: phase.phase_order)
    current_phase = None
    for phase in ordered_phases:
        phase_steps = [
            row for row in required
            if row.step_template.phase_id == phase.id and row.status != "completed"
        ]
        if phase_steps:
            current_phase = phase.title
            break
    return total, completed, percent, current_phase


def _summary(roadmap: UserRoadmap) -> UserRoadmapSummary:
    total, completed, percent, current_phase = _progress_counts(roadmap)
    return UserRoadmapSummary(
        id=roadmap.id,
        career_id=roadmap.career_id,
        career_name=roadmap.career.name,
        category=roadmap.career.category,
        title=roadmap.template.title,
        template_version=roadmap.template.version,
        status=roadmap.status,
        total_steps=total,
        completed_steps=completed,
        completion_percent=percent,
        current_phase=current_phase,
        skill_profile_was_empty=roadmap.skill_profile_was_empty,
        created_at=roadmap.created_at,
        updated_at=roadmap.updated_at,
        completed_at=roadmap.completed_at,
    )


@router.get("/templates", response_model=list[RoadmapTemplateRead])
def list_roadmap_templates(database: Session = Depends(get_db)):
    """List careers with curated roadmap templates so the career picker stays accurate."""
    templates = database.scalars(
        select(RoadmapTemplate)
        .options(joinedload(RoadmapTemplate.career))
        .order_by(RoadmapTemplate.career_id)
    ).unique().all()
    # Keep the latest version for each career; templates are shared catalog data.
    latest: dict[int, RoadmapTemplate] = {}
    for template in templates:
        previous = latest.get(template.career_id)
        if previous is None or template.version > previous.version:
            latest[template.career_id] = template
    return [
        RoadmapTemplateRead(
            career_id=template.career_id,
            career_name=template.career.name,
            category=template.career.category,
            difficulty_level=template.career.difficulty_level,
            title=template.title,
            summary=template.summary,
            version=template.version,
        )
        for template in latest.values()
    ]


@router.get("/me", response_model=list[UserRoadmapSummary])
def list_my_roadmaps(
    user: User = Depends(get_current_user),
    database: Session = Depends(get_db),
):
    roadmaps = database.scalars(
        _roadmap_query().where(UserRoadmap.user_id == user.id).order_by(UserRoadmap.updated_at.desc())
    ).unique().all()
    return [_summary(roadmap) for roadmap in roadmaps]


@router.post("", response_model=UserRoadmapDetail, status_code=status.HTTP_200_OK)
def create_or_resume_roadmap(
    payload: RoadmapCreate,
    user: User = Depends(get_current_user),
    database: Session = Depends(get_db),
):
    career = database.get(Career, payload.career_id)
    if career is None:
        raise HTTPException(status_code=404, detail="Career not found.")

    existing = database.scalar(
        _roadmap_query().where(
            UserRoadmap.user_id == user.id,
            UserRoadmap.career_id == career.id,
        )
    )
    if existing is not None:
        return _detail(existing)

    template = database.scalar(
        select(RoadmapTemplate)
        .where(RoadmapTemplate.career_id == career.id)
        .order_by(RoadmapTemplate.version.desc())
        .limit(1)
    )
    if template is None:
        raise HTTPException(status_code=404, detail="A roadmap for this career is not available yet.")

    # This uses the exact same career requirements, proficiency labels, and
    # strong/developing/gap rules as GET /api/careers/{id}/skill-gap.
    gap = calculate_skill_gap(career.id, user.id, database)
    gap_by_skill = {item.skill_id: item for item in gap.skills}
    has_no_saved_skills = database.scalar(
        select(UserSkill.id).where(UserSkill.user_id == user.id).limit(1)
    ) is None
    roadmap = UserRoadmap(
        user_id=user.id,
        career_id=career.id,
        template_id=template.id,
        skill_profile_was_empty=has_no_saved_skills,
    )
    all_template_steps = [
        step
        for phase in sorted(template.phases, key=lambda item: item.phase_order)
        for step in sorted(phase.steps, key=lambda item: item.step_order)
    ]
    # Within each phase, focus first on non-strong skills, highest catalog
    # priority, then lowest self-reported proficiency. Keep authored phase order.
    personalized = []
    for phase in sorted(template.phases, key=lambda item: item.phase_order):
        phase_steps = sorted(phase.steps, key=lambda item: item.step_order)
        # Keep authored prerequisite order in Foundations. Personalize the core
        # skill phase by putting non-strong, high-priority gaps first.
        if phase.phase_order == 2:
            phase_steps.sort(key=lambda step: _personalization_key(step, gap_by_skill))
        personalized.extend(phase_steps)
    if not all_template_steps:
        raise HTTPException(status_code=500, detail="The selected roadmap template has no steps.")

    for order, step in enumerate(personalized, start=1):
        gap_item = gap_by_skill.get(step.skill_id) if step.skill_id is not None else None
        roadmap.step_progress.append(UserRoadmapStepProgress(
            step_template=step,
            personalized_order=order,
            is_optional=bool(gap_item and gap_item.status == "strong"),
            proficiency_level_at_creation=gap_item.proficiency_level if gap_item else None,
            priority_at_creation=gap_item.priority if gap_item else None,
            target_level_at_creation=gap_item.target_level if gap_item else None,
            estimated_minutes_at_creation=_personalized_estimate(step.estimated_minutes, gap_item),
        ))
    database.add(roadmap)
    try:
        database.commit()
    except IntegrityError:
        database.rollback()
        # A second simultaneous request can win the unique user/career key.
        existing = database.scalar(
            _roadmap_query().where(UserRoadmap.user_id == user.id, UserRoadmap.career_id == career.id)
        )
        if existing is not None:
            return _detail(existing)
        raise HTTPException(status_code=409, detail="The roadmap could not be created. Please try again.")

    saved = database.scalar(_roadmap_query().where(UserRoadmap.id == roadmap.id))
    return _detail(saved)


def _personalization_key(step: RoadmapStepTemplate, gap_by_skill: dict):
    item = gap_by_skill.get(step.skill_id) if step.skill_id is not None else None
    if item is None:
        return (1, 1, 0, step.step_order)
    return (
        1 if item.status == "strong" else 0,
        PRIORITY_ORDER.get(item.priority, 1),
        item.proficiency_level,
        step.step_order,
    )


def _personalized_estimate(base_minutes: int, gap_item) -> int:
    """Give a beginner more practice time and keep estimates frozen per roadmap."""
    if gap_item is None:
        return base_minutes
    if gap_item.status == "strong":
        return max(30, ceil(base_minutes * 0.35))
    if gap_item.status == "developing":
        return max(30, ceil(base_minutes * (1.2 if gap_item.proficiency_level == 1 else 0.8)))
    return ceil(base_minutes * 1.35)


def _detail(roadmap: UserRoadmap) -> UserRoadmapDetail:
    # The role-specific priority/target were captured at roadmap creation in
    # each step's progress row; expose those stable values with its instructions.
    phases = []
    for phase in sorted(roadmap.template.phases, key=lambda item: item.phase_order):
        phase_rows = [
            row for row in roadmap.step_progress
            if row.step_template.phase_id == phase.id
        ]
        phase_rows.sort(key=lambda row: row.personalized_order)
        required_rows = [row for row in phase_rows if not row.is_optional]
        completed_required = sum(row.status == "completed" for row in required_rows)
        phase_total = len(required_rows)
        step_reads = []
        for row in phase_rows:
            step = row.step_template
            step_reads.append(RoadmapStepRead(
                id=row.id,
                template_step_id=step.id,
                order=row.personalized_order,
                title=step.title,
                instructions=step.instructions,
                completion_criteria=step.completion_criteria,
                prerequisites=step.prerequisites,
                estimated_minutes=(
                    row.estimated_minutes_at_creation
                    if roadmap.template.version >= 3 else None
                ),
                skill_id=step.skill_id,
                skill_name=step.skill.name if step.skill else None,
                proficiency_level_at_creation=row.proficiency_level_at_creation,
                target_level=row.target_level_at_creation,
                priority=row.priority_at_creation,
                is_optional=row.is_optional,
                status=row.status,
                started_at=row.started_at,
                completed_at=row.completed_at,
                resource_title=step.resource_title,
                resource_url=step.resource_url,
                resource_search=step.resource_search,
            ))
        phases.append(RoadmapPhaseRead(
            id=phase.id,
            order=phase.phase_order,
            title=phase.title,
            objective=phase.objective,
            description=phase.description,
            total_steps=phase_total,
            completed_steps=completed_required,
            completion_percent=round(completed_required / phase_total * 100) if phase_total else 100,
            steps=step_reads,
        ))

    summary = _summary(roadmap)
    return UserRoadmapDetail(
        **summary.model_dump(),
        career_description=roadmap.career.description,
        career_difficulty=roadmap.career.difficulty_level,
        summary=roadmap.template.summary,
        phases=phases,
        personalization_note=(
            "No skills were saved when this roadmap was created, so it starts with the foundations. "
            "You can add skills on the Skill Gap page; this existing roadmap will not reorder itself."
            if roadmap.skill_profile_was_empty
            else "Step order reflects your saved career skill gaps at creation. Strong skills are optional review; "
                 "the roadmap will not reorder if you later edit your skill profile."
        ),
    )


@router.get("/{roadmap_id}", response_model=UserRoadmapDetail)
def get_my_roadmap(
    roadmap_id: int,
    user: User = Depends(get_current_user),
    database: Session = Depends(get_db),
):
    roadmap = database.scalar(
        _roadmap_query().where(UserRoadmap.id == roadmap_id, UserRoadmap.user_id == user.id)
    )
    if roadmap is None:
        raise HTTPException(status_code=404, detail="Roadmap not found.")
    return _detail(roadmap)


@router.patch("/{roadmap_id}/steps/{step_id}", response_model=UserRoadmapDetail)
def update_my_roadmap_step(
    roadmap_id: int,
    step_id: int,
    payload: RoadmapStepStatusUpdate,
    user: User = Depends(get_current_user),
    database: Session = Depends(get_db),
):
    roadmap = database.scalar(
        _roadmap_query().where(UserRoadmap.id == roadmap_id, UserRoadmap.user_id == user.id)
    )
    if roadmap is None:
        raise HTTPException(status_code=404, detail="Roadmap not found.")

    progress = database.scalar(
        select(UserRoadmapStepProgress)
        .join(UserRoadmapStepProgress.roadmap)
        .where(
            UserRoadmapStepProgress.id == step_id,
            UserRoadmapStepProgress.roadmap_id == roadmap.id,
            UserRoadmap.user_id == user.id,
        )
    )
    if progress is None or progress.step_template.phase.template_id != roadmap.template_id:
        raise HTTPException(status_code=404, detail="Roadmap step not found.")

    now = datetime.now(timezone.utc)
    progress.status = payload.status
    progress.started_at = None if payload.status == "not_started" else (progress.started_at or now)
    progress.completed_at = now if payload.status == "completed" else None
    roadmap.updated_at = now

    required = [row for row in roadmap.step_progress if not row.is_optional]
    all_done = bool(required) and all(row.status == "completed" for row in required)
    roadmap.status = "completed" if all_done else "active"
    roadmap.completed_at = now if all_done else None
    database.commit()

    updated = database.scalar(_roadmap_query().where(UserRoadmap.id == roadmap.id))
    return _detail(updated)
