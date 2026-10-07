# Career Mentor Backend

A FastAPI application for the Career Counseling Project, using SQLite and SQLAlchemy.

## Run locally

From this `backend/` directory, activate the virtual environment and start the server:

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

The API runs at http://127.0.0.1:8000. Interactive docs are at http://127.0.0.1:8000/docs.

## Environment setup

Copy `.env.example` to `.env` and set `JWT_SECRET_KEY` to a private random value. For example, generate one with:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Keep `.env` private; it is ignored by Git. The example file contains only a placeholder. `ACCESS_TOKEN_EXPIRE_MINUTES` controls how long a login token remains valid.

Install dependencies in a new virtual environment with:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Authentication endpoints

- `POST /api/auth/register` — create an account with `full_name`, `email`, `password`, and optional `education` and `experience_level`. The response contains safe profile fields only.
- `POST /api/auth/login` — verify `email` and `password`; returns a bearer access token and safe user profile.
- `GET /api/auth/me` — provide `Authorization: Bearer <access_token>` to read the authenticated user's profile.

Passwords are stored as Argon2 hashes. Login tokens are signed JWTs with the user's ID and an expiration time; the signing secret comes from `JWT_SECRET_KEY`.

## Career and skill catalog

The ignored SQLite file is `career_mentor.db`. On startup, SQLAlchemy ensures that `careers`, `skills`, `career_skills`, `database_checks`, `users`, `assessment_responses`, and `career_recommendations` exist, then seeds 59 career paths and 120 skills. Careers and skills share a many-to-many relationship through `career_skills`.

- `GET /api/careers` — list careers.
- `GET /api/careers/{career_id}` — career details, including associated skills.
- `GET /api/skills` — list skills.
- `GET /api/health` — backend health check.
- `GET /api/db-test` — database connection check.

## Career assessment

The question catalog contains 20 required multiple-choice questions across interests, strengths, work style, technology, communication, business, creativity, problem solving, and career preferences. The questions are kept in `app/assessment_data.py` so they can be extended independently of the response storage. Each signed-in user's answers are stored in `assessment_responses`; a unique constraint on `(user_id, question_id)` means retaking the assessment updates answers instead of creating duplicates.

All assessment endpoints require `Authorization: Bearer <access_token>`:

- `GET /api/assessment/questions` — return the question text, category, type, required flag, and allowed option values and labels.
- `POST /api/assessment/submit` — save the complete assessment. Send `{ "answers": [{ "question_id": "q01", "selected_option": "build_solutions" }] }` with one answer for each required question.
- `GET /api/assessment/my-results` — return only the signed-in user's saved answers and completion count.

Unknown question IDs, duplicate question IDs in one submission, missing required answers, and invalid option values return HTTP 422. Users cannot read or submit another user's assessment.

## Career recommendations

The recommendation engine uses transparent, rule-based scoring; it does not call an AI service. Each answer option contributes weighted interest signals such as technology, data, communication, creativity, finance, service, and education. It also normalizes a score for each of the assessment's nine question dimensions. Career-category and role-specific profiles are compared with both sets of scores using cosine similarity (85% signal fit and 15% dimension fit). The explanation on each result is built from the strongest shared signals. All 59 catalog careers are scored and ranked; the API returns the top 10.

The `career_recommendations` table stores one current score and rank for each `(user_id, career_id)` pair. Completing or retaking the assessment recalculates and updates these rows, so repeated submissions do not add duplicate recommendation records.

- `GET /api/recommendations` — protected; calculate and return the signed-in user's top career matches, including match percentage, explanation, and related catalog skills. Returns HTTP 409 with a clear message until all assessment questions have answers.


## Browser origins and CORS

The Vite development server proxies API calls locally. For a separate frontend origin (for example, a production deployment), list its exact origin in `FRONTEND_ORIGINS` in `backend/.env`, separated by commas. Do not include URL paths in this list. Local Vite and preview origins are allowed by default. SQLite foreign-key enforcement is enabled on each database connection.
