"""Transparent rule-based matching from assessment options to career profiles."""

from collections import defaultdict
from math import sqrt

from .assessment_data import ASSESSMENT_QUESTIONS

# Each option contributes points to one or more career-interest signals. More
# than one answer contributes to a signal, so no individual answer determines a career.
OPTION_SIGNALS = {
    "q01": {
        "build_solutions": {"software": 2, "technology": 1, "problem_solving": 1},
        "find_patterns": {"data": 2, "analytical": 2, "problem_solving": 1},
        "help_people": {"people": 2, "service": 2, "communication": 1},
        "grow_ideas": {"business": 2, "leadership": 1, "marketing": 1},
    },
    "q02": {
        "make_digital": {"technology": 2, "software": 2},
        "interpret_data": {"data": 3, "analytical": 1},
        "create_campaign": {"marketing": 2, "creative": 2, "communication": 1},
        "teach_skill": {"education": 3, "communication": 1, "people": 1},
    },
    "q03": {
        "logical_thinking": {"analytical": 2, "problem_solving": 2, "technology": 1},
        "clear_explanations": {"communication": 2, "education": 1, "service": 1},
        "organizing": {"organization": 2, "administration": 1, "business": 1},
        "fresh_ideas": {"creative": 3, "marketing": 1},
    },
    "q04": {
        "focused_independent": {"analytical": 1, "software": 1, "data": 1},
        "collaborative": {"people": 1, "communication": 1, "business": 1},
        "people_facing": {"people": 2, "service": 2, "communication": 1},
        "varied_fast": {"business": 1, "sales": 1, "organization": 1},
    },
    "q05": {
        "very_comfortable": {"technology": 3, "software": 1, "data": 1},
        "comfortable_guidance": {"technology": 2, "administration": 1},
        "somewhat": {"technology": 1, "administration": 1},
        "not_primary": {"technology": -1},
    },
    "q06": {
        "numbers_data": {"data": 2, "analytical": 2, "finance": 1},
        "people": {"people": 2, "communication": 1, "service": 1},
        "visuals_content": {"creative": 2, "marketing": 1, "communication": 1},
        "systems_processes": {"organization": 2, "business": 1, "administration": 1},
    },
    "q07": {
        "very_interested": {"software": 3, "technology": 2},
        "curious": {"software": 1, "technology": 2},
        "use_tools": {"technology": 1, "data": 1, "administration": 1},
        "other_focus": {"software": -1},
    },
    "q08": {
        "investigate": {"problem_solving": 2, "analytical": 2, "cybersecurity": 1},
        "ask_people": {"people": 2, "communication": 1, "service": 1},
        "try_options": {"problem_solving": 2, "business": 1},
        "reframe": {"creative": 2, "problem_solving": 1, "marketing": 1},
    },
    "q09": {
        "energized": {"communication": 2, "people": 2, "sales": 1},
        "comfortable": {"communication": 2, "people": 1},
        "written_first": {"communication": 1, "creative": 1, "administration": 1},
        "developing": {"communication": 1},
    },
    "q10": {
        "enjoy": {"finance": 3, "data": 1, "analytical": 1},
        "learn": {"finance": 2, "business": 1},
        "some_context": {"finance": 1, "business": 1, "data": 1},
        "not_much": {"finance": -1},
    },
    "q11": {
        "love_teaching": {"education": 3, "communication": 2, "people": 1},
        "happy_to_help": {"service": 2, "people": 1, "communication": 1},
        "written_guides": {"creative": 1, "communication": 1, "education": 1},
        "prefer_other": {"education": -1},
    },
    "q12": {
        "product_working": {"software": 2, "technology": 1, "problem_solving": 1},
        "insight_found": {"data": 2, "analytical": 2, "business": 1},
        "person_helped": {"service": 2, "people": 2, "education": 1},
        "goal_reached": {"business": 2, "leadership": 2, "organization": 1},
    },
    "q13": {
        "detailed_review": {"analytical": 2, "finance": 1, "organization": 1},
        "plan_coordination": {"leadership": 2, "organization": 2, "business": 1},
        "open_ended_creation": {"creative": 3, "marketing": 1},
        "solve_request": {"service": 2, "communication": 1, "problem_solving": 1},
    },
    "q14": {
        "structured": {"organization": 2, "administration": 2, "finance": 1},
        "mostly_structured": {"organization": 2, "business": 1},
        "mostly_open": {"creative": 1, "business": 1},
        "open_ended": {"creative": 2, "marketing": 1},
    },
    "q15": {
        "improve_process": {"business": 2, "organization": 2, "problem_solving": 1},
        "understand_customers": {"people": 1, "marketing": 1, "sales": 1, "service": 1},
        "manage_resources": {"finance": 2, "organization": 2, "business": 1},
        "support_team": {"hr": 2, "people": 1, "organization": 1},
    },
    "q16": {
        "design_experience": {"creative": 3, "technology": 1},
        "write_stories": {"creative": 2, "marketing": 2, "communication": 1},
        "make_visuals": {"creative": 3, "marketing": 1},
        "creative_not_focus": {"creative": -1},
    },
    "q17": {
        "steady": {"analytical": 1, "organization": 1},
        "planned_busy": {"organization": 2, "business": 1},
        "fast_changing": {"sales": 1, "service": 1, "business": 1},
        "mix": {"organization": 1, "business": 1},
    },
    "q18": {
        "very_interested": {"cybersecurity": 3, "risk": 2, "problem_solving": 1},
        "curious": {"cybersecurity": 2, "risk": 1, "technology": 1},
        "practical": {"risk": 1, "organization": 1, "administration": 1},
        "other_interest": {"cybersecurity": -1},
    },
    "q19": {
        "useful_tools": {"technology": 2, "software": 1, "problem_solving": 1},
        "better_decisions": {"business": 2, "data": 1, "finance": 1},
        "people_progress": {"people": 2, "education": 1, "hr": 1},
        "clear_communication": {"communication": 2, "creative": 1, "marketing": 1},
    },
    "q20": {
        "technology_data": {"technology": 2, "software": 1, "data": 1, "cybersecurity": 1},
        "business_finance": {"business": 1, "finance": 1, "organization": 1},
        "people_services": {"people": 1, "service": 1, "sales": 1, "hr": 1, "education": 1},
        "creative_admin": {"creative": 1, "marketing": 1, "administration": 1, "organization": 1},
    },
}

# Shared category profiles keep the model understandable. Role-specific additions
# distinguish related careers (for example, an analyst from a data scientist).
CATEGORY_PROFILES = {
    "Software Development": {"software": 3, "technology": 2, "problem_solving": 2, "analytical": 1},
    "Technology & IT": {"technology": 2, "problem_solving": 2, "organization": 1},
    "Data & AI": {"data": 3, "analytical": 3, "technology": 2, "problem_solving": 1},
    "Cybersecurity & Cloud": {"technology": 2, "cybersecurity": 3, "risk": 2, "problem_solving": 2},
    "Business & Management": {"business": 3, "organization": 2, "leadership": 2, "communication": 1},
    "Customer Support & BPO": {"service": 3, "people": 2, "communication": 2},
    "Sales": {"sales": 3, "people": 2, "communication": 2, "business": 1},
    "Marketing & Digital Marketing": {"marketing": 3, "creative": 1, "communication": 2, "data": 1},
    "Design & Creative": {"creative": 3, "communication": 1, "marketing": 1},
    "Finance & Accounting": {"finance": 3, "analytical": 2, "organization": 2, "data": 1},
    "Human Resources & Recruitment": {"hr": 3, "people": 2, "communication": 2, "organization": 1},
    "Administration & Office": {"administration": 3, "organization": 3, "communication": 1},
    "Education & Training": {"education": 3, "communication": 2, "people": 2, "organization": 1},
}

ROLE_ADDITIONS = {
    "software engineer": {"software": 2, "analytical": 1},
    "frontend developer": {"creative": 1, "software": 1},
    "backend developer": {"software": 2, "analytical": 1},
    "full stack developer": {"software": 2, "technology": 1},
    "mobile app developer": {"software": 2, "creative": 1},
    "qa engineer / software tester": {"analytical": 2, "problem_solving": 2},
    "it support specialist": {"service": 2, "communication": 1},
    "database administrator": {"data": 2, "organization": 1},
    "network administrator": {"technology": 1, "cybersecurity": 1},
    "systems administrator": {"technology": 1, "cybersecurity": 1},
    "data analyst": {"data": 2, "business": 1},
    "data scientist": {"data": 2, "analytical": 1},
    "machine learning engineer": {"software": 1, "data": 1},
    "ai engineer": {"software": 1, "data": 1},
    "nlp engineer": {"communication": 1, "software": 1},
    "computer vision engineer": {"software": 1, "analytical": 1},
    "business intelligence analyst": {"data": 2, "business": 2},
    "devops engineer": {"software": 1, "cybersecurity": 1},
    "cloud engineer": {"technology": 1, "cybersecurity": 1},
    "cybersecurity analyst": {"analytical": 1, "risk": 1},
    "security engineer": {"software": 1, "problem_solving": 1},
    "soc analyst": {"analytical": 2, "risk": 1},
    "business analyst": {"data": 1, "problem_solving": 1},
    "project manager": {"leadership": 2, "organization": 1},
    "product manager": {"business": 1, "creative": 1, "leadership": 1},
    "operations executive": {"organization": 2, "business": 1},
    "customer support representative": {"service": 1, "people": 1},
    "customer service executive": {"service": 1, "communication": 1},
    "call center representative": {"communication": 1, "service": 1},
    "technical support representative": {"technology": 1, "problem_solving": 1},
    "chat support representative": {"communication": 1, "organization": 1},
    "email support executive": {"communication": 1, "organization": 1},
    "customer success executive": {"people": 2, "business": 1},
    "quality assurance executive": {"analytical": 2, "organization": 1},
    "call center team lead": {"leadership": 2, "organization": 1},
    "sales representative": {"people": 1, "business": 1},
    "business development representative": {"sales": 1, "business": 1},
    "account executive": {"business": 1, "people": 1},
    "digital marketing specialist": {"marketing": 1, "data": 1},
    "seo specialist": {"data": 2, "analytical": 1},
    "social media manager": {"creative": 1, "communication": 1},
    "content marketing specialist": {"creative": 1, "communication": 1},
    "ui/ux designer": {"technology": 1, "problem_solving": 1},
    "graphic designer": {"creative": 1, "marketing": 1},
    "video editor": {"creative": 1, "marketing": 1},
    "content writer": {"communication": 1, "marketing": 1},
    "copywriter": {"communication": 1, "marketing": 1},
    "accountant": {"finance": 2, "organization": 1},
    "financial analyst": {"finance": 2, "data": 1},
    "banking officer": {"finance": 1, "service": 1},
    "hr executive": {"hr": 2, "organization": 1},
    "recruiter / talent acquisition specialist": {"hr": 2, "sales": 1},
    "administrative assistant": {"administration": 1, "communication": 1},
    "office assistant": {"administration": 1, "service": 1},
    "data entry operator": {"administration": 1, "analytical": 1},
    "teacher": {"education": 2, "communication": 1},
    "online tutor": {"education": 2, "people": 1},
    "computer instructor": {"education": 1, "technology": 1},
}

CAREER_DIMENSION_GROUP = {
    "Software Development": "technology",
    "Technology & IT": "technology",
    "Data & AI": "data",
    "Cybersecurity & Cloud": "cybersecurity",
    "Business & Management": "business",
    "Customer Support & BPO": "people",
    "Sales": "sales",
    "Marketing & Digital Marketing": "marketing",
    "Design & Creative": "creative",
    "Finance & Accounting": "finance",
    "Human Resources & Recruitment": "people",
    "Administration & Office": "operations",
    "Education & Training": "education",
}

# Category-level profiles add a smaller, separate part to the overall score.
# The signal profile below remains the stronger influence.
DIMENSION_PROFILES = {
    "technology": {"interests": 1, "strengths": 0.9, "work_style": 0.5, "technology": 1, "communication": 0.2, "business": 0.2, "creativity": 0.2, "problem_solving": 1, "career_preferences": 0.8},
    "data": {"interests": 1, "strengths": 1, "work_style": 0.6, "technology": 0.8, "communication": 0.2, "business": 0.6, "creativity": 0.1, "problem_solving": 1, "career_preferences": 0.8},
    "cybersecurity": {"interests": 0.8, "strengths": 0.9, "work_style": 0.8, "technology": 1, "communication": 0.2, "business": 0.2, "creativity": 0.1, "problem_solving": 1, "career_preferences": 0.8},
    "business": {"interests": 0.8, "strengths": 0.9, "work_style": 0.8, "technology": 0.3, "communication": 0.7, "business": 1, "creativity": 0.2, "problem_solving": 0.6, "career_preferences": 0.9},
    "people": {"interests": 0.8, "strengths": 0.8, "work_style": 0.8, "technology": 0.2, "communication": 1, "business": 0.3, "creativity": 0.2, "problem_solving": 0.4, "career_preferences": 0.8},
    "sales": {"interests": 0.8, "strengths": 0.6, "work_style": 0.7, "technology": 0.2, "communication": 1, "business": 0.8, "creativity": 0.3, "problem_solving": 0.5, "career_preferences": 0.8},
    "marketing": {"interests": 0.9, "strengths": 0.7, "work_style": 0.6, "technology": 0.3, "communication": 0.8, "business": 0.7, "creativity": 0.9, "problem_solving": 0.4, "career_preferences": 0.8},
    "creative": {"interests": 0.9, "strengths": 0.8, "work_style": 0.5, "technology": 0.2, "communication": 0.6, "business": 0.2, "creativity": 1, "problem_solving": 0.4, "career_preferences": 0.8},
    "finance": {"interests": 0.8, "strengths": 0.9, "work_style": 0.8, "technology": 0.3, "communication": 0.3, "business": 0.9, "creativity": 0.1, "problem_solving": 0.7, "career_preferences": 0.8},
    "operations": {"interests": 0.5, "strengths": 0.9, "work_style": 1, "technology": 0.3, "communication": 0.5, "business": 0.7, "creativity": 0.1, "problem_solving": 0.6, "career_preferences": 0.8},
    "education": {"interests": 0.9, "strengths": 0.8, "work_style": 0.6, "technology": 0.2, "communication": 1, "business": 0.2, "creativity": 0.3, "problem_solving": 0.5, "career_preferences": 0.9},
}

SIGNAL_LABELS = {
    "technology": "comfort exploring technology",
    "software": "interest in building software",
    "data": "interest in working with data",
    "analytical": "analytical and detail-focused strengths",
    "problem_solving": "a step-by-step problem-solving approach",
    "cybersecurity": "interest in security and protecting systems",
    "risk": "attention to risk and prevention",
    "business": "interest in business decisions and outcomes",
    "leadership": "interest in coordinating people toward goals",
    "organization": "a preference for organized, structured work",
    "people": "interest in working with people",
    "service": "a service-minded approach to helping others",
    "communication": "confidence or interest in communication",
    "sales": "interest in building customer relationships",
    "marketing": "interest in reaching and understanding audiences",
    "creative": "creative and visual interests",
    "finance": "interest in financial information and numbers",
    "hr": "interest in supporting teams and employee experience",
    "administration": "comfort with practical office and process work",
    "education": "interest in teaching and helping others learn",
}

DEFAULT_CATEGORY_PROFILE = {"problem_solving": 1, "business": 1, "communication": 1}


def assessment_signal_scores(responses) -> dict[str, float]:
    """Sum the weighted signals represented by the user's saved options."""
    question_ids = {question["id"] for question in ASSESSMENT_QUESTIONS}
    scores: dict[str, float] = defaultdict(float)
    for response in responses:
        question_id = response.question_id
        if question_id not in question_ids:
            continue
        for signal, points in OPTION_SIGNALS.get(question_id, {}).get(response.selected_option, {}).items():
            scores[signal] += points
    return dict(scores)


def assessment_dimension_scores(responses) -> dict[str, float]:
    """Normalize selected-option signals within each of the nine question groups."""
    question_by_id = {question["id"]: question for question in ASSESSMENT_QUESTIONS}
    totals: dict[str, float] = defaultdict(float)
    maximums: dict[str, float] = defaultdict(float)
    for response in responses:
        question = question_by_id.get(response.question_id)
        if question is None:
            continue
        option_map = OPTION_SIGNALS.get(response.question_id, {})
        def strength(option_value):
            return sum(max(points, 0) for points in option_map.get(option_value, {}).values())
        selected_strength = strength(response.selected_option)
        best_strength = max((strength(option["value"]) for option in question["options"]), default=0)
        dimension = question["category"]
        totals[dimension] += selected_strength
        maximums[dimension] += best_strength
    return {
        dimension: round(total / maximums[dimension], 3) if maximums[dimension] else 0
        for dimension, total in totals.items()
    }


def career_profile(career) -> dict[str, float]:
    """Combine a shared category profile with a small role-specific profile."""
    profile = dict(CATEGORY_PROFILES.get(career.category, DEFAULT_CATEGORY_PROFILE))
    for signal, weight in ROLE_ADDITIONS.get(career.name.lower(), {}).items():
        profile[signal] = profile.get(signal, 0) + weight
    return profile


def score_career(signal_scores: dict[str, float], career, dimension_scores=None) -> tuple[float, list[str]]:
    """Return cosine-style fit and the strongest positive reasons for that fit."""
    profile = career_profile(career)
    positive_user_signals = {key: max(value, 0) for key, value in signal_scores.items()}
    user_norm = sqrt(sum(value * value for value in positive_user_signals.values()))
    profile_norm = sqrt(sum(value * value for value in profile.values()))
    if user_norm == 0 or profile_norm == 0:
        return 0.0, []

    contributions = {
        signal: user_value * profile.get(signal, 0)
        for signal, user_value in positive_user_signals.items()
        if user_value > 0 and profile.get(signal, 0) > 0
    }
    signal_cosine = sum(contributions.values()) / (user_norm * profile_norm)
    dimension_group = CAREER_DIMENSION_GROUP.get(career.category, "business")
    dimension_profile = DIMENSION_PROFILES[dimension_group]
    dimensions = dimension_scores or {}
    dimension_norm = sqrt(sum(value * value for value in dimensions.values()))
    dimension_profile_norm = sqrt(sum(value * value for value in dimension_profile.values()))
    dimension_cosine = (
        sum(value * dimension_profile.get(dimension, 0) for dimension, value in dimensions.items())
        / (dimension_norm * dimension_profile_norm)
        if dimension_norm and dimension_profile_norm
        else 0
    )
    cosine = (signal_cosine * 0.85) + (dimension_cosine * 0.15)
    reasons = [SIGNAL_LABELS[key] for key, _ in sorted(contributions.items(), key=lambda item: item[1], reverse=True)[:3]]
    return round(max(0.0, min(cosine * 100, 100.0)), 1), reasons


def score_all_careers(careers, responses):
    """Score and sort the complete catalog; stable IDs break exact score ties."""
    signals = assessment_signal_scores(responses)
    dimensions = assessment_dimension_scores(responses)
    scored = []
    for career in careers:
        score, reasons = score_career(signals, career, dimensions)
        scored.append({"career": career, "match_score": score, "reasons": reasons})
    return sorted(scored, key=lambda item: (-item["match_score"], item["career"].id))


def explanation_for(reasons: list[str]) -> str:
    if not reasons:
        return "Your answers did not strongly favor a specific work style, so use this match as a starting point for exploration."
    if len(reasons) == 1:
        return f"This role aligns with your {reasons[0]}."
    return f"This role aligns with your {reasons[0]}, {reasons[1]}, and {reasons[2] if len(reasons) > 2 else 'related interests'}."
