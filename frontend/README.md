# AI Career Mentor Frontend

React and Vite frontend for the Career Counseling Project.

## Run locally

From this directory, install dependencies once, copy `.env.example` to `.env.local`, and start Vite:

```powershell
npm install
Copy-Item .env.example .env.local
npm run dev
```

Start FastAPI separately from `backend/`. During development, Vite proxies `/api` requests to `VITE_API_BASE_URL`. Production builds call that configured API origin directly, so the backend must allow the deployed frontend origin in `FRONTEND_ORIGINS`.

Build for production with `npm run build`.

## Routes

- `/` - landing page.
- `/register` - create an account.
- `/login` - sign in.
- `/dashboard` - protected user dashboard with assessment and recommendation links.
- `/assessment` - protected 20-question assessment; retakes update saved responses.
- `/recommendations` - protected top 10 career matches with scores, explanations, skills, and expandable career details.
- `/careers/:careerId/skill-gap` - protected profile editor and career-specific skill readiness comparison.

The bearer token is kept in `sessionStorage` for the current tab session and removed on logout. The assessment and recommendations use authenticated FastAPI endpoints; no recommendation mock data is used in the signed-in results page.
