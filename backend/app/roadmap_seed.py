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
from .roadmap_catalog import CAREER_ROADMAPS, ROADMAP_VERSION

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


def _learning_step(skill: Skill, career_name: str, position: int, priority: str,
                   prerequisites: str | None, role_focus: str) -> RoadmapStepTemplate:
    resource = VERIFIED_SKILL_RESOURCES.get(skill.name)
    base_minutes = {"high": 240, "medium": 180, "low": 120}.get(priority, 150)
    return RoadmapStepTemplate(
        skill=skill,
        step_order=position,
        title=f"Build {skill.name} for {career_name}",
        instructions=(
            f"{skill.description} Practice it in a small, role-related exercise. "
            f"For this career, focus on: {role_focus}"
        ),
        completion_criteria=(
            f"Save a work sample demonstrating {skill.name}, verify it against the task, "
            "and write a short note describing your approach and result."
        ),
        prerequisites=prerequisites,
        estimated_minutes=base_minutes,
        resource_title=resource[0] if resource else None,
        resource_url=resource[1] if resource else None,
        resource_search=(
            None if resource else
            f"Search for free official documentation or public learning materials about {skill.name}"
        ),
    )


def seed_roadmap_catalog(database: Session) -> int:
    """Seed the complete role-specific catalog as an immutable new version."""
    inserted = 0
    for career in database.scalars(select(Career).order_by(Career.id)).all():
        profile = CAREER_ROADMAPS.get(career.slug)
        if profile is None:
            raise ValueError(f"No curated roadmap profile for catalog career: {career.slug}")

        existing = database.scalar(
            select(RoadmapTemplate.id).where(
                RoadmapTemplate.career_id == career.id,
                RoadmapTemplate.version == ROADMAP_VERSION,
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
        foundations = profile["foundations"]
        missing = set(foundations) - skills_by_name.keys()
        if missing:
            raise ValueError(
                f"Foundation skill(s) are not linked to {career.name}: {', '.join(sorted(missing))}"
            )
        if not requirements:
            raise ValueError(f"Career has no linked skills: {career.name}")

        template = RoadmapTemplate(
            career=career,
            version=ROADMAP_VERSION,
            title=f"{career.name} Career Roadmap",
            summary=profile["focus"],
        )
        foundation_phase = RoadmapPhaseTemplate(
            phase_order=1,
            title="Foundations",
            objective=f"Build the essential starting skills for {career.name}.",
            description=f"Follow these prerequisites in order before moving into the wider role skill set.",
        )
        foundation_steps = []
        for position, name in enumerate(foundations, start=1):
            skill, priority, _target = skills_by_name[name]
            prior = foundations[:position - 1]
            foundation_steps.append(_learning_step(
                skill, career.name, position, priority,
                f"Complete first: {', '.join(prior)}" if prior else "No prerequisite; this is a starting skill.",
                profile["focus"],
            ))
        foundation_phase.steps = foundation_steps

        foundation_names = set(foundations)
        remaining = [row for row in requirements if row[0].name not in foundation_names]
        remaining.sort(key=lambda row: (PRIORITY_ORDER.get(row[1], 1), row[0].name.casefold()))
        core_phase = RoadmapPhaseTemplate(
            phase_order=2,
            title="Role-specific skills",
            objective=f"Practice the skills connected to {career.name} in the order that best fits your current profile.",
            description="Catalog priorities and your saved skill levels personalize this phase when you start the roadmap.",
        )
        core_phase.steps = [
            _learning_step(
                skill, career.name, position, priority,
                "Complete or review the Foundations phase first.", profile["focus"],
            )
            for position, (skill, priority, _target) in enumerate(remaining, start=1)
        ]

        workflow_title, workflow_instructions, workflow_criteria = profile["workflow"]
        workflow_phase = RoadmapPhaseTemplate(
            phase_order=3,
            title="Practice the work",
            objective=f"Apply the day-to-day workflow used in {career.name}.",
            description="Use a fictional, public, or otherwise authorized scenario and record the evidence behind your decisions.",
        )
        workflow_phase.steps = [RoadmapStepTemplate(
            step_order=1,
            title=workflow_title,
            instructions=workflow_instructions,
            completion_criteria=workflow_criteria,
            prerequisites="Complete the Foundations phase and review the relevant role-specific skill steps.",
            estimated_minutes=180,
            resource_search=f"Search for a free introductory practice scenario for {career.name}",
        )]

        project_title, project_instructions, project_criteria = profile["project"]
        project_phase = RoadmapPhaseTemplate(
            phase_order=4,
            title="Career-specific project",
            objective=f"Create a practical example that combines skills used in {career.name}.",
            description="Produce a small, reviewable work sample. Follow the criteria rather than relying on course completion alone.",
        )
        project_phase.steps = [RoadmapStepTemplate(
            step_order=1,
            title=project_title,
            instructions=project_instructions,
            completion_criteria=project_criteria,
            prerequisites="Complete or review the preceding skill and work-practice phases.",
            estimated_minutes=360,
            resource_search=f"Search for a free public example project related to {career.name}",
        )]

        preparation_phase = RoadmapPhaseTemplate(
            phase_order=5,
            title="Career preparation",
            objective="Organize evidence of your learning and prepare to discuss the work clearly.",
            description="This final step helps turn practice into a concise portfolio or interview example.",
        )
        preparation_phase.steps = [RoadmapStepTemplate(
            step_order=1,
            title=f"Present your {career.name} work",
            instructions=profile["prep"],
            completion_criteria=(
                "Save a one-page case study, list three skills demonstrated, include evidence or a work sample, "
                "and write two questions for a mentor, recruiter, or next learning session."
            ),
            prerequisites="Complete the career-specific project before preparing this summary.",
            estimated_minutes=90,
            resource_search=f"Search for free portfolio or interview preparation guidance for {career.name}",
        )]

        template.phases = [
            foundation_phase, core_phase, workflow_phase, project_phase, preparation_phase,
        ]
        database.add(template)
        inserted += 1

    database.commit()
    return inserted
