from sqlalchemy import select, update
from sqlalchemy.orm import Session

from .catalog import CAREER_DATA, SKILL_DATA
from .models import Career, Skill, career_skills


def career_skill_priority(position: int) -> tuple[str, int]:
    """Use the catalog order to store career-specific skill importance."""
    if position < 3:
        return "high", 3
    if position < 6:
        return "medium", 2
    return "low", 1


def seed_data(database: Session) -> None:
    """Insert or update the catalog without creating duplicate rows."""
    skill_names = [name for name, _, _ in SKILL_DATA]
    if len(skill_names) != len(set(skill_names)):
        raise ValueError("The skill catalog contains duplicate names.")

    skills_by_name = {}
    for name, category, description in SKILL_DATA:
        skill = database.scalar(select(Skill).where(Skill.name == name))
        if skill is None:
            skill = Skill(name=name, category=category, description=description)
            database.add(skill)
        else:
            # Keep the existing row and ID, while refreshing its catalog details.
            skill.category = category
            skill.description = description
        skills_by_name[name] = skill

    database.flush()
    career_slugs = [career[1] for career in CAREER_DATA]
    if len(career_slugs) != len(set(career_slugs)):
        raise ValueError("The career catalog contains duplicate slugs.")

    for name, slug, description, category, difficulty, career_skill_names in CAREER_DATA:
        missing_skills = set(career_skill_names) - skills_by_name.keys()
        if missing_skills:
            raise ValueError(f"Unknown skills for {name}: {', '.join(sorted(missing_skills))}")

        career = database.scalar(select(Career).where(Career.slug == slug))
        if career is None:
            career = Career(name=name, slug=slug)
            database.add(career)

        # Update the existing row in place so its ID remains stable.
        career.name = name
        career.description = description
        career.category = category
        career.difficulty_level = difficulty
        career.skills = [skills_by_name[skill_name] for skill_name in career_skill_names]
        database.flush()

        # CAREER_DATA keeps required skills in curated relevance order. Persist
        # that career-specific priority on the existing career_skills rows.
        for position, skill_name in enumerate(career_skill_names):
            priority, target_level = career_skill_priority(position)
            database.execute(
                update(career_skills)
                .where(
                    career_skills.c.career_id == career.id,
                    career_skills.c.skill_id == skills_by_name[skill_name].id,
                )
                .values(priority=priority, target_level=target_level)
            )

    database.commit()
