# Career Counseling Project / AI Career Mentor

A JavaScript React frontend and Python FastAPI backend for exploring career paths. The current product includes account registration and login, a protected 20-question career assessment, a catalog of 59 careers and 120 skills, an explainable recommendation engine, self-reported skill gap comparisons, and career-specific roadmaps for all 59 careers.

## Project structure

- `frontend/` - React + Vite single-page application.
- `backend/` - FastAPI API, SQLAlchemy models, and local SQLite database.
- `docs/` - project documentation and notes.

## Run locally

Start the API in one terminal:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

Start the frontend in another terminal:

```powershell
cd frontend
npm install
npm run dev
```

The local development frontend is `http://localhost:5173`; the API is `http://127.0.0.1:8000`. The Vite server proxies `/api` calls to the backend. See each folder's README and `.env.example` for configuration.

## Current user journey

1. Register and sign in; authentication uses Argon2 password hashes and JWT bearer tokens.
2. Complete or retake the 20-question assessment; answers are private to the signed-in user.
3. View the top 10 career matches from all 59 catalog careers. The rule-based score combines weighted answer signals and normalized question dimensions. Match percentages indicate profile similarity, not probability of success or a guaranteed career outcome.
4. Explore a recommended career, save current skills and proficiency levels, and review weighted Strong, Developing, and Gap categories on its skill gap page.
5. Select any catalog career, follow its ordered learning phases, and save step progress. The roadmap is based on the career's existing required skills and the user's profile at creation; users can also choose a career without taking the assessment. Previously started roadmaps keep their original template version and progress.

Skill readiness is an internal comparison metric, not a guarantee of job readiness. The recommendation engine and roadmap personalization are rule-based and do not call an AI or paid API. Roadmaps cover all 59 catalog careers; daily task scheduling, quizzes, and AI mentor conversations are not implemented.
