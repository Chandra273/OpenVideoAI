from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext
from passlib.hash import pbkdf2_sha256

from .config import settings

# pwd_context = CryptContext(...) — passlib context to hash/verify passwords securely using bcrypt.
# verify_password(...) — compares a plaintext password to a stored hash.
# get_password_hash(...) — produces a secure hash to store.
# create_access_token(subject, expires_delta) — builds a JWT with sub (subject) and exp claims, signed using settings.SECRET_KEY and HS256. We encode user id as the subject.

# Use pbkdf2_sha256 in development to avoid bcrypt backend compatibility and 72-byte limits.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pbkdf2_sha256.verify(plain_password, hashed_password)
    except Exception:
        # fallback to CryptContext verify for compatibility
        return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    try:
        return pbkdf2_sha256.hash(password)
    except Exception:
        # fallback to CryptContext
        return pwd_context.hash(password)


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {"sub": subject, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt
