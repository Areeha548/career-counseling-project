"""Seed the first version of selected career roadmaps without changing catalog rows."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import (
    Career,
    RoadmapPhaseTemplate,
    RoadmapStepTemplate,
    RoadmapTemplate,
    Skill,
    career_skills,
)
from .roadmap_data import ROADMAP_TEMPLATES, VERIFIED_SKILL_RESOURCES

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def _skill_step(skill: Skill, career_name: str, order: int) -> RoadmapStepTemplate:
    resource = VERIFIED_SKILL_RESOURCES.get(skill.name)
    return RoadmapStepTemplate(
        skill=skill,
        step_order=order,
        title=f"Practice {skill.name}",
        instructions=(
            f"{skill.description} Start with a small exercise, then apply {skill.name} "
            f"to a task connected to {career_name}."
        ),
        completion_criteria=(
            f"Save one work sample that demonstrates {skill.name}; note the goal, "
            "the steps you took, and the result in 2–3 sentences."
        ),
        resource_title=resource[0] if resource else None,
        resource_url=resource[1] if resource else None,
    )


def seed_roadmap_templates(database: Session) -> int:
    """Insert absent template versions; existing versions stay immutable for users."""
    inserted = 0
    for definition in ROADMAP_TEMPLATES:
        career = database.scalar(select(Career).where(Career.slug == definition["career_slug"]))
        if career is None:
            raise ValueError(f"Roadmap career does not exist: {definition['career_slug']}")

        existing = database.scalar(
            select(RoadmapTemplate).where(
                RoadmapTemplate.career_id == career.id,
                RoadmapTemplate.version == definition["version"],
            )
        )
        if existing is not None:
            continue

        requirements = database.execute(
            select(Skill, career_skills.c.priority, career_skills.c.target_level)
            .join(career_skills, career_skills.c.skill_id == Skill.id)
            .where(career_skills.c.career_id == career.id)
        ).all()
        skills_by_name = {skill.name: (skill, priority, target) for skill, priority, target in requirements}
        foundations = definition["foundation_skills"]
        missing = set(foundations) - skills_by_name.keys()
        if missing:
            raise ValueError(f"Foundation skill(s) not linked to {career.name}: {', '.join(sorted(missing))}")

        template = RoadmapTemplate(
            career=career,
            version=definition["version"],
            title=definition["title"],
            summary=definition["summary"],
        )
        foundation_rows = [skills_by_name[name] for name in foundations]
        other_rows = [row for row in requirements if row[0].name not in foundations]
        other_rows.sort(key=lambda row: (PRIORITY_ORDER.get(row[1], 1), row[0].name.casefold()))

        foundation_phase = RoadmapPhaseTemplate(
            phase_order=1,
            title="Foundations",
            objective="Build the essential knowledge and habits needed for this career.",
            description=f"Begin with the foundations that support your path toward {career.name}.",
        )
        foundation_phase.steps = [
            _skill_step(skill, career.name, position)
            for position, (skill, _priority, _target) in enumerate(foundation_rows, start=1)
        ]

        core_phase = RoadmapPhaseTemplate(
            phase_order=2,
            title="Core career skills",
            objective="Practice the remaining skills connected to this career profile.",
            description="Work through role-specific requirements, giving higher-priority gaps attention first.",
        )
        core_phase.steps = [
            _skill_step(skill, career.name, position)
            for position, (skill, _priority, _target) in enumerate(other_rows, start=1)
        ]

        project = definition["project"]
        project_phase = RoadmapPhaseTemplate(
            phase_order=3,
            title="Practical project",
            objective="Combine your skills in a concrete piece of work.",
            description="Use this project to practice, review your decisions, and produce evidence of your learning.",
        )
        project_phase.steps = [RoadmapStepTemplate(
            step_order=1,
            title=project["title"],
            instructions=project["instructions"],
            completion_criteria=project["criteria"],
        )]

        preparation_phase = RoadmapPhaseTemplate(
            phase_order=4,
            title="Career preparation",
            objective="Explain your work clearly and prepare for the next career step.",
            description="Organize your evidence and reflect on what you are ready to learn next.",
        )
        preparation_phase.steps = [RoadmapStepTemplate(
            step_order=1,
            title="Prepare your career story",
            instructions=definition["preparation"],
            completion_criteria=(
                "Save a one-page case study or work summary, list three skills demonstrated, "
                "and write two questions to explore in your next learning or interview conversation."
            ),
        )]

        template.phases = [foundation_phase, core_phase, project_phase, preparation_phase]
        database.add(template)
        inserted += 1

    database.commit()
    return inserted
