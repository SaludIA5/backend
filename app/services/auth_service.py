# app/services/auth_service.py
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.databases.postgresql.db import get_db
from app.databases.postgresql.models import User

# Si tienes prefijo /api, ajusta el tokenUrl a ese prefijo:
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_prefix}/auth/login" if hasattr(settings, "api_prefix") else "/auth/login", auto_error=False)

def _decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.security_config.secret_key,
        algorithms=[settings.security_config.algorithm],
    )

async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    bearer_token: str | None = Depends(oauth2_scheme),  # puede venir o no
) -> User:
    """
    Extrae token desde Authorization Bearer o cookie 'access_token'.
    Decodifica y carga el usuario desde la DB.
    """
    token = bearer_token or request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = _decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    res = await db.execute(select(User).where(User.id == int(user_id)))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# ---- Helpers de autorización por rol ----
async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Admin only")
    return current_user

async def require_medical_role(current_user: User = Depends(get_current_user)) -> User:
    if not (getattr(current_user, "is_doctor", False) or getattr(current_user, "is_chief_doctor", False)):
        raise HTTPException(status_code=403, detail="Medical role required")
    return current_user
