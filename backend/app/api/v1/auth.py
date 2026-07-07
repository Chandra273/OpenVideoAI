from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...models.user import User
from ...schemas.user import UserCreate, Token, UserRead
from ...core.security import get_password_hash, verify_password, create_access_token
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


def _validate_password(password: str) -> None:
    # bcrypt has a 72-byte input limit; enforce a reasonable max password length
    if not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password is required")
    encoded = password.encode("utf-8")
    if len(encoded) > 72:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password too long (max 72 bytes)")


@router.post("/register", response_model=UserRead)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    # Instrumentation to help diagnose unexpected password sizes
    try:
        pw_bytes = user_in.password.encode("utf-8")
    except Exception:
        pw_bytes = b""
    # Debug output (temporary) to diagnose unexpected password content
    print(f"DEBUG register: email={user_in.email} pw_repr={repr(user_in.password)} pw_bytes_len={len(pw_bytes)}")
    logger.info("Register attempt: email=%s password_len=%d password_repr=%s", user_in.email, len(pw_bytes), repr(user_in.password))
    _validate_password(user_in.password)
    try:
        hashed = get_password_hash(user_in.password)
    except ValueError as e:
        # passlib/bcrypt may raise ValueError for invalid inputs; surface as 400
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    user = User(email=user_in.email, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(user_in: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    token = create_access_token(subject=str(user.id))
    return {"access_token": token, "token_type": "bearer"}
