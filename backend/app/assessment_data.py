"""Question catalog for the first version of the career assessment."""


ASSESSMENT_QUESTIONS = [
    {
        "id": "q01", "category": "interests", "question_type": "single_choice", "required": True,
        "question_text": "Which kind of problem would you most enjoy solving?",
        "options": [
            {"value": "build_solutions", "label": "Designing or building a useful solution"},
            {"value": "find_patterns", "label": "Finding patterns in information"},
            {"value": "help_people", "label": "Helping someone work through a challenge"},
            {"value": "grow_ideas", "label": "Turning an idea into a successful plan"},
        ],
    },
    {
        "id": "q02", "category": "interests", "question_type": "single_choice", "required": True,
        "question_text": "Which activity sounds most interesting to you?",
        "options": [
            {"value": "make_digital", "label": "Making a digital product or tool"},
            {"value": "interpret_data", "label": "Exploring data to answer a question"},
            {"value": "create_campaign", "label": "Creating a campaign or story people notice"},
            {"value": "teach_skill", "label": "Teaching someone a useful new skill"},
        ],
    },
    {
        "id": "q03", "category": "strengths", "question_type": "single_choice", "required": True,
        "question_text": "What do people most often rely on you for?",
        "options": [
            {"value": "logical_thinking", "label": "Thinking logically and spotting what is wrong"},
            {"value": "clear_explanations", "label": "Explaining things in a clear, patient way"},
            {"value": "organizing", "label": "Keeping plans and details organized"},
            {"value": "fresh_ideas", "label": "Bringing fresh ideas and a creative eye"},
        ],
    },
    {
        "id": "q04", "category": "work_style", "question_type": "single_choice", "required": True,
        "question_text": "Which work environment would help you do your best?",
        "options": [
            {"value": "focused_independent", "label": "Quiet time for focused, independent work"},
            {"value": "collaborative", "label": "A collaborative team solving things together"},
            {"value": "people_facing", "label": "A role with regular conversations and support"},
            {"value": "varied_fast", "label": "A fast-moving day with varied priorities"},
        ],
    },
    {
        "id": "q05", "category": "technology", "question_type": "single_choice", "required": True,
        "question_text": "How comfortable are you learning new technology?",
        "options": [
            {"value": "very_comfortable", "label": "Very comfortable; I enjoy exploring new tools"},
            {"value": "comfortable_guidance", "label": "Comfortable when I have a clear guide"},
            {"value": "somewhat", "label": "Somewhat; I prefer familiar tools"},
            {"value": "not_primary", "label": "It is not a major interest for me right now"},
        ],
    },
    {
        "id": "q06", "category": "interests", "question_type": "single_choice", "required": True,
        "question_text": "Which would you rather spend time working with?",
        "options": [
            {"value": "numbers_data", "label": "Numbers, data, and evidence"},
            {"value": "people", "label": "People, conversations, and relationships"},
            {"value": "visuals_content", "label": "Visuals, words, and creative content"},
            {"value": "systems_processes", "label": "Systems, processes, and practical details"},
        ],
    },
    {
        "id": "q07", "category": "technology", "question_type": "single_choice", "required": True,
        "question_text": "How interested are you in learning programming?",
        "options": [
            {"value": "very_interested", "label": "Very interested; I want to build software"},
            {"value": "curious", "label": "Curious; I would like to understand the basics"},
            {"value": "use_tools", "label": "I prefer using technology tools without coding"},
            {"value": "other_focus", "label": "I am more interested in a different kind of work"},
        ],
    },
    {
        "id": "q08", "category": "problem_solving", "question_type": "single_choice", "required": True,
        "question_text": "When something goes wrong, what is your first instinct?",
        "options": [
            {"value": "investigate", "label": "Investigate the cause step by step"},
            {"value": "ask_people", "label": "Ask people involved and understand their needs"},
            {"value": "try_options", "label": "Try a few practical options quickly"},
            {"value": "reframe", "label": "Look at the problem from a new angle"},
        ],
    },
    {
        "id": "q09", "category": "communication", "question_type": "single_choice", "required": True,
        "question_text": "How do you feel about communicating with people at work?",
        "options": [
            {"value": "energized", "label": "Energized; I enjoy frequent conversations"},
            {"value": "comfortable", "label": "Comfortable, especially in small groups"},
            {"value": "written_first", "label": "I prefer thoughtful written communication"},
            {"value": "developing", "label": "I am building confidence and open to practicing"},
        ],
    },
    {
        "id": "q10", "category": "business", "question_type": "single_choice", "required": True,
        "question_text": "Would you enjoy reviewing financial or business information?",
        "options": [
            {"value": "enjoy", "label": "Yes, I enjoy numbers and making sense of them"},
            {"value": "learn", "label": "I would be interested in learning how"},
            {"value": "some_context", "label": "Sometimes, when it connects to a real decision"},
            {"value": "not_much", "label": "Not especially; other topics interest me more"},
        ],
    },
    {
        "id": "q11", "category": "communication", "question_type": "single_choice", "required": True,
        "question_text": "How would you feel about teaching or explaining concepts to others?",
        "options": [
            {"value": "love_teaching", "label": "I would love to help people understand"},
            {"value": "happy_to_help", "label": "I am happy to help one person at a time"},
            {"value": "written_guides", "label": "I would rather create clear written guides"},
            {"value": "prefer_other", "label": "I prefer work with less explaining or teaching"},
        ],
    },
    {
        "id": "q12", "category": "career_preferences", "question_type": "single_choice", "required": True,
        "question_text": "What kind of progress would feel most rewarding?",
        "options": [
            {"value": "product_working", "label": "Seeing something I built work well"},
            {"value": "insight_found", "label": "Finding an insight that guides a decision"},
            {"value": "person_helped", "label": "Knowing I helped a person succeed"},
            {"value": "goal_reached", "label": "Helping a team reach an important goal"},
        ],
    },
    {
        "id": "q13", "category": "strengths", "question_type": "single_choice", "required": True,
        "question_text": "Which type of task would you choose first?",
        "options": [
            {"value": "detailed_review", "label": "Carefully checking details for accuracy"},
            {"value": "plan_coordination", "label": "Planning work and coordinating people"},
            {"value": "open_ended_creation", "label": "Creating something with room to experiment"},
            {"value": "solve_request", "label": "Responding to a request and finding a helpful answer"},
        ],
    },
    {
        "id": "q14", "category": "work_style", "question_type": "single_choice", "required": True,
        "question_text": "Do you prefer structured tasks or open-ended creative work?",
        "options": [
            {"value": "structured", "label": "Clear steps, routines, and expectations"},
            {"value": "mostly_structured", "label": "A clear plan with some flexibility"},
            {"value": "mostly_open", "label": "A goal to work toward, with freedom in how"},
            {"value": "open_ended", "label": "Open-ended work where I can experiment"},
        ],
    },
    {
        "id": "q15", "category": "business", "question_type": "single_choice", "required": True,
        "question_text": "Which business challenge sounds most engaging?",
        "options": [
            {"value": "improve_process", "label": "Making an everyday process work better"},
            {"value": "understand_customers", "label": "Understanding what customers need"},
            {"value": "manage_resources", "label": "Keeping budgets and resources accurate"},
            {"value": "support_team", "label": "Helping a team stay organized and supported"},
        ],
    },
    {
        "id": "q16", "category": "creativity", "question_type": "single_choice", "required": True,
        "question_text": "Which creative activity appeals to you most?",
        "options": [
            {"value": "design_experience", "label": "Designing how a digital experience looks and feels"},
            {"value": "write_stories", "label": "Writing stories, articles, or persuasive messages"},
            {"value": "make_visuals", "label": "Creating graphics, video, or visual content"},
            {"value": "creative_not_focus", "label": "Creative work is not my main focus"},
        ],
    },
    {
        "id": "q17", "category": "career_preferences", "question_type": "single_choice", "required": True,
        "question_text": "What pace of work suits you best?",
        "options": [
            {"value": "steady", "label": "A steady pace with time to focus"},
            {"value": "planned_busy", "label": "Busy but planned, with clear priorities"},
            {"value": "fast_changing", "label": "Fast-moving and changing throughout the day"},
            {"value": "mix", "label": "A mix of focused time and active periods"},
        ],
    },
    {
        "id": "q18", "category": "problem_solving", "question_type": "single_choice", "required": True,
        "question_text": "How do you feel about protecting information and preventing risks?",
        "options": [
            {"value": "very_interested", "label": "Very interested; I like anticipating risks"},
            {"value": "curious", "label": "Curious; I would like to learn more"},
            {"value": "practical", "label": "I focus on following good procedures"},
            {"value": "other_interest", "label": "Other kinds of challenges interest me more"},
        ],
    },
    {
        "id": "q19", "category": "career_preferences", "question_type": "single_choice", "required": True,
        "question_text": "What would you most like your work to contribute?",
        "options": [
            {"value": "useful_tools", "label": "Useful products, technology, or reliable systems"},
            {"value": "better_decisions", "label": "Better-informed decisions and business results"},
            {"value": "people_progress", "label": "People's growth, confidence, or wellbeing"},
            {"value": "clear_communication", "label": "Ideas and information people can understand"},
        ],
    },
    {
        "id": "q20", "category": "career_preferences", "question_type": "single_choice", "required": True,
        "question_text": "Which direction would you be most curious to explore next?",
        "options": [
            {"value": "technology_data", "label": "Technology, software, data, or cybersecurity"},
            {"value": "business_finance", "label": "Business, operations, finance, or project work"},
            {"value": "people_services", "label": "Customer support, sales, HR, or education"},
            {"value": "creative_admin", "label": "Design, marketing, writing, or organized office work"},
        ],
    },
]

QUESTION_BY_ID = {question["id"]: question for question in ASSESSMENT_QUESTIONS}
