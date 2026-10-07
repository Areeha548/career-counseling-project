from datetime import datetime, timedelta, timezone
from pathlib import Path
import os

import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash

BACKEND_DIRECTORY = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIRECTORY / ".env")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Return a one-way Argon2 hash for a password."""
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Check a submitted password against its stored hash."""
    return password_hasher.verify(password, password_hash)


def create_access_token(user_id: int) -> str:
    """Create a signed JWT that identifies one user and expires soon."""
    if not JWT_SECRET_KEY:
        raise RuntimeError("Set JWT_SECRET_KEY in backend/.env before using authentication.")

    now = datetime.now(timezone.utc)
    claims = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(claims, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def read_access_token(token: str) -> str:
    """Validate a JWT and return its user ID subject."""
    if not JWT_SECRET_KEY:
        raise RuntimeError("Set JWT_SECRET_KEY in backend/.env before using authentication.")

    claims = jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM],
        options={"require": ["sub", "exp"]},
    )
    return claims["sub"]
