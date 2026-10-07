from contextlib import asynccontextmanager
import os

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from . import models
from .auth import router as auth_router
from .assessment import router as assessment_router
from .recommendations import router as recommendations_router
from .skill_gap import router as skill_gap_router
from .skill_profiles import router as skill_profiles_router
from .database import Base, SessionLocal, engine, ensure_career_skill_metadata, get_db
from .schemas import CareerDetail, CareerRead, SkillRead
from .seed import seed_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables and seed starter data when the API starts."""
    Base.metadata.create_all(bind=engine)
    ensure_career_skill_metadata()
    with SessionLocal() as database:
        seed_data(database)
    yield


app = FastAPI(title="Career Mentor API", lifespan=lifespan)
configured_origins = os.getenv(
    "FRONTEND_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:4173,http://127.0.0.1:4173",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in configured_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "OPTIONS"],
    allow_headers=["Accept", "Authorization", "Content-Type"],
)
app.include_router(auth_router)
app.include_router(assessment_router)
app.include_router(recommendations_router)
app.include_router(skill_profiles_router)
app.include_router(skill_gap_router)


@app.get("/api/health")
def health_check():
    """Confirm that the backend is running."""
    return {
        "status": "ok",
        "message": "Career Mentor backend is running.",
    }


@app.get("/api/db-test")
def database_test(database: Session = Depends(get_db)):
    """Query the verification table to confirm SQLite is reachable."""
    database.execute(select(models.DatabaseCheck.id).limit(1)).all()
    return {
        "status": "ok",
        "message": "Database connection successful.",
    }


@app.get("/api/careers", response_model=list[CareerRead])
def list_careers(database: Session = Depends(get_db)):
    """Return all available career paths."""
    return database.scalars(select(models.Career).order_by(models.Career.id)).all()


@app.get("/api/skills", response_model=list[SkillRead])
def list_skills(database: Session = Depends(get_db)):
    """Return all available skills."""
    return database.scalars(select(models.Skill).order_by(models.Skill.id)).all()


@app.get("/api/careers/{career_id}", response_model=CareerDetail)
def get_career(career_id: int, database: Session = Depends(get_db)):
    """Return one career and the skills connected to it."""
    career = database.scalar(
        select(models.Career)
        .options(selectinload(models.Career.skills))
        .where(models.Career.id == career_id)
    )
    if career is None:
        raise HTTPException(status_code=404, detail="Career not found")
    return career
