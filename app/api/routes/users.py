from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.hash import bcrypt
from app.databases.postgresql.db import get_db
from app.databases.postgresql.models import User

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/")
async def create_user(name: str, email: str, password: str, role: str = "Otro", db: AsyncSession = Depends(get_db)):
    hashed_password = bcrypt.hash(password)
    new_user = User(name=name, email=email, hashed_password=hashed_password, role=role)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.get("/")
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()
