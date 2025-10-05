from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from passlib.hash import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.databases.postgresql.db import get_db
from app.databases.postgresql.models import User
from app.schemas import LoginRequest, Token

router = APIRouter(prefix="/auth", tags=["auth"])


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
    is_doctor: bool = False,
    is_chief_doctor: bool = False,
) -> str:
    expire = datetime.utcnow() + (
        expires_delta
        if expires_delta
        else timedelta(minutes=settings.security_config.access_token_expire_minutes)
    )
    to_encode = {
        "sub": subject,
        "exp": expire,
        "is_doctor": is_doctor,
        "is_chief_doctor": is_chief_doctor,
    }
    return jwt.encode(
        to_encode,
        settings.security_config.secret_key,
        algorithm=settings.security_config.algorithm,
    )


@router.post("/login", response_model=Token)
async def login(payload: LoginRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user or not bcrypt.verify(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    token = create_access_token(
        subject=str(user.id),
        is_doctor=user.is_doctor,
        is_chief_doctor=user.is_chief_doctor,
    )
    return Token(access_token=token)
