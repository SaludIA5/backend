from typing import Annotated, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.databases.postgresql.db import get_db
from app.databases.postgresql.models import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserOut, UserPage, UserPageMeta, UserUpdate
from app.services.auth_service import get_current_user, require_admin

router = APIRouter(prefix="/users", tags=["users"])


def _total_pages(total: int, size: int) -> int:
    return (total + size - 1) // size if size else 1


# SIGNUP (público) — fuerza roles en False para evitar escalamiento
@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        return await UserRepository.create(
            db,
            name=payload.name,
            email=payload.email,
            rut=payload.rut,
            password=payload.password,
            # Ignoramos flags del payload por seguridad:
            is_chief_doctor=payload.is_chief_doctor,
            is_doctor=payload.is_doctor,
            turn=payload.turn,
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Email ya registrado")


# LIST (requiere login)
@router.get("/", response_model=UserPage)
async def list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = None,
    _current: Annotated[User, Depends(get_current_user)] = None,
):
    items, total = await UserRepository.list_paginated(
        db, page=page, page_size=page_size, search=search
    )
    return UserPage(
        items=items,
        meta=UserPageMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=_total_pages(total, page_size),
        ),
    )


# GET by ID (requiere login)
@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current: Annotated[User, Depends(get_current_user)] = None,
):
    user = await UserRepository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# GET by email (requiere login)
@router.get("/by-email/{email}", response_model=UserOut)
async def get_user_by_email(
    email: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current: Annotated[User, Depends(get_current_user)] = None,
):
    user = await UserRepository.get_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# UPDATE (solo admin)
@router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
):
    user = await UserRepository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        return await UserRepository.update_partial(
            db, user, **payload.model_dump(exclude_unset=True)
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Email ya registrado")


# DELETE (solo admin)
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
):
    user = await UserRepository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await UserRepository.hard_delete(db, user)
    return None


# BY TURN (requiere login)
@router.get("/by-turn", response_model=Dict[str, List[UserOut]], status_code=status.HTTP_200_OK)
async def list_people_grouped_by_turn(
    db: Annotated[AsyncSession, Depends(get_db)],
    _current: Annotated[User, Depends(get_current_user)] = None,
):
    grouped = await UserRepository.group_doctors_and_chiefs_by_turn(db)
    return {turn: [UserOut.model_validate(u) for u in users] for turn, users in grouped.items()}
