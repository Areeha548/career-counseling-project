"""Curated starter roadmap content for selected existing career catalog entries.

Add a new definition by career slug; career and skill rows remain in the catalog.
Increment ``version`` when published content needs a new immutable template.
"""

ROADMAP_TEMPLATES = [
    {
        "career_slug": "web-developer", "version": 2,
        "title": "Web Developer Starter Roadmap",
        "summary": "Build the foundations of accessible websites, then publish a complete web project.",
        "foundation_skills": ["HTML", "CSS"],
        "project": {
            "title": "Publish a responsive small-business website",
            "instructions": "Plan and build a multi-section website for a fictional local business. Use semantic page structure, responsive styling, and a small interactive feature where appropriate.",
            "criteria": "Publish at least three linked sections or pages; check the layout at mobile and desktop widths; include a short README explaining the audience and design choices.",
        },
        "preparation": "Prepare a portfolio entry that explains the website's audience, accessible choices, responsive behavior, and one improvement you would make next.",
    },
    {
        "career_slug": "software-engineer", "version": 2,
        "title": "Software Engineer Starter Roadmap",
        "summary": "Practice programming fundamentals, problem solving, testing, and delivery through a documented application.",
        "foundation_skills": ["Programming", "Python", "Data Structures"],
        "project": {
            "title": "Build and test a small useful application",
            "instructions": "Choose a small problem, design its inputs and outputs, implement a working program, and organize the code so another person can follow it.",
            "criteria": "Deliver a working application, at least five meaningful automated or repeatable checks, and a README with setup steps and two design decisions.",
        },
        "preparation": "Create a portfolio write-up that shows the problem, a simple design diagram, test approach, Git history, and one trade-off you considered.",
    },
    {
        "career_slug": "data-analyst", "version": 2,
        "title": "Data Analyst Starter Roadmap",
        "summary": "Move from reliable data handling to clear analysis and a decision-focused dashboard.",
        "foundation_skills": ["Excel", "SQL"],
        "project": {
            "title": "Analyze a public dataset and present a finding",
            "instructions": "Choose a small public dataset, check its quality, answer a practical question with analysis, and present the result in a concise dashboard or report.",
            "criteria": "Document the source and at least three data-quality checks; show three findings supported by figures; include one chart and a written recommendation.",
        },
        "preparation": "Prepare a case-study summary that states the business question, data limits, analysis steps, and how a decision-maker could use the result.",
    },
    {
        "career_slug": "ai-engineer", "version": 2,
        "title": "AI Engineer Starter Roadmap",
        "summary": "Build programming and machine-learning foundations, then evaluate and explain a small AI-enabled project.",
        "foundation_skills": ["Python"],
        "project": {
            "title": "Train and evaluate a small machine-learning model",
            "instructions": "Use a suitable public learning dataset to create a small supervised-learning experiment. Keep training and evaluation separate, then explain what the model can and cannot show.",
            "criteria": "Provide a reproducible notebook or script, a baseline and evaluated model metric, a brief error review, and notes on data limitations. Do not present the result as production-ready AI.",
        },
        "preparation": "Write a project brief covering the user problem, data source, evaluation method, limitations, and responsible-use considerations.",
    },
    {
        "career_slug": "frontend-developer", "version": 2,
        "title": "Frontend Developer Starter Roadmap",
        "summary": "Progress from web standards to interactive, accessible interfaces and a polished portfolio project.",
        "foundation_skills": ["HTML", "CSS", "JavaScript"],
        "project": {
            "title": "Build an accessible interactive career profile site",
            "instructions": "Create a responsive multi-section site with reusable interface pieces and a useful interaction, such as filtering or form feedback.",
            "criteria": "Complete the key interaction with keyboard and pointer; check mobile and desktop layouts; use semantic labels; document the components and one accessibility improvement.",
        },
        "preparation": "Publish a portfolio entry with a live or locally reproducible demo, screenshots at two widths, and a short explanation of accessibility and component choices.",
    },
    {
        "career_slug": "backend-developer", "version": 2,
        "title": "Backend Developer Starter Roadmap",
        "summary": "Learn server-side programming, data modeling, APIs, and tests through a small documented service.",
        "foundation_skills": ["Programming", "Python", "SQL"],
        "project": {
            "title": "Create a documented data-backed API",
            "instructions": "Design a small API around one clear resource. Validate inputs, persist records in a relational database, and return predictable errors.",
            "criteria": "Implement at least three endpoints, validate normal and invalid requests, include five API checks, and document example requests plus database relationships.",
        },
        "preparation": "Prepare a technical overview showing endpoint design, data relationships, validation, testing, and how you would protect sensitive configuration.",
    },
    {
        "career_slug": "ui-ux-designer", "version": 2,
        "title": "UI/UX Designer Starter Roadmap",
        "summary": "Practice user research, information structure, interface design, prototyping, and design validation.",
        "foundation_skills": ["Communication", "Critical Thinking", "Market Research"],
        "project": {
            "title": "Design and test a focused product flow",
            "instructions": "Choose one user need, map the current challenge, sketch alternatives, then create a clickable prototype for one complete flow.",
            "criteria": "Show a problem statement, at least three early sketches, a linked prototype, feedback from three review sessions, and a short list of changes made from that feedback.",
        },
        "preparation": "Create a case study that explains the user need, constraints, design iterations, feedback, accessibility decisions, and what you would test next.",
    },
    {
        "career_slug": "cybersecurity-analyst", "version": 2,
        "title": "Cybersecurity Analyst Starter Roadmap",
        "summary": "Build security fundamentals and investigation habits using safe, authorized learning exercises.",
        "foundation_skills": ["Cybersecurity Fundamentals", "Networking Basics", "Linux"],
        "project": {
            "title": "Write a safe security alert investigation",
            "instructions": "Use a public training scenario or synthetic logs to document how an analyst would triage an alert. Do not probe systems without explicit authorization.",
            "criteria": "Record the alert context, at least five investigation observations, a severity rationale, containment recommendation, and a clear incident summary using synthetic or authorized data only.",
        },
        "preparation": "Prepare a sample incident report that separates observed evidence from assumptions and includes a timeline, impact, response, and follow-up actions.",
    },
]

# URLs below were opened and checked during implementation. Other steps omit a
# resource link until a dependable page has been verified.
VERIFIED_SKILL_RESOURCES = {
    "HTML": ("MDN Learn Web Development", "https://developer.mozilla.org/en-US/docs/Learn_web_development"),
    "CSS": ("MDN Learn Web Development", "https://developer.mozilla.org/en-US/docs/Learn_web_development"),
    "JavaScript": ("MDN Learn Web Development", "https://developer.mozilla.org/en-US/docs/Learn_web_development"),
    "React": ("React Learn", "https://react.dev/learn"),
    "Python": ("The Python Tutorial", "https://docs.python.org/3/tutorial/"),
    "SQL": ("SQLBolt interactive lessons", "https://sqlbolt.com/"),
    "FastAPI": ("FastAPI Tutorial", "https://fastapi.tiangolo.com/tutorial/"),
    "Machine Learning": ("Google Machine Learning Crash Course", "https://developers.google.com/machine-learning/crash-course"),
    "Cybersecurity Fundamentals": ("OWASP Top 10", "https://owasp.org/projects/top-ten"),
    "Figma": ("Figma Resource Library", "https://www.figma.com/resource-library/"),
    "UI/UX Design": ("W3C WAI: Evaluating Web Accessibility", "https://www.w3.org/WAI/test-evaluate/"),
    "Git": ("Pro Git book", "https://git-scm.com/book/en/v2"),
    "Software Testing": ("Python unittest documentation", "https://docs.python.org/3/library/unittest.html"),
    "Pandas": ("pandas getting started tutorials", "https://pandas.pydata.org/docs/getting_started/intro_tutorials/index.html"),
}
