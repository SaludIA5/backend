from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.databases.postgresql.db import get_db
from app.databases.postgresql.models import User
from app.repositories import EpisodeRepository, PatientRepository
from app.schemas import (
    EpisodeWithTeamAndDoctor,
    PatientCreate,
    PatientOut,
    PatientPage,
    PatientPageMeta,
    PatientUpdate,
    UserOut,
)
from app.services.auth_service import (
    get_current_user,
    require_admin,
    require_medical_role,
)

router = APIRouter(prefix="/patients", tags=["patients"])


def _total_pages(total: int, size: int) -> int:
    return (total + size - 1) // size if size else 1


# CREATE
@router.post("/", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
async def create_patient(
    payload: PatientCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_medical_role)],
):
    try:
        return await PatientRepository.create(
            db, name=payload.name, rut=payload.rut, age=payload.age
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail="RUT ya registrado")


# LIST
@router.get("/", response_model=PatientPage)
async def list_patients(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = None,
    active: bool | None = None,
    _current: Annotated[User, Depends(get_current_user)] = None,
):
    items, total = await PatientRepository.list_paginated(
        db, page=page, page_size=page_size, search=search, active=active
    )
    return PatientPage(
        items=items,
        meta=PatientPageMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=_total_pages(total, page_size),
        ),
    )


# GET BY ID
@router.get("/{patient_id}", response_model=PatientOut)
async def get_patient(
    patient_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current: Annotated[User, Depends(get_current_user)] = None,
):
    patient = await PatientRepository.get_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


# UPDATE
@router.patch("/{patient_id}", response_model=PatientOut)
async def update_patient(
    patient_id: int,
    payload: PatientUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_medical_role)],
):
    patient = await PatientRepository.get_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    try:
        return await PatientRepository.update_partial(
            db, patient, **payload.model_dump(exclude_unset=True)
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail="RUT ya registrado")


# DELETE
@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
):
    patient = await PatientRepository.get_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    await PatientRepository.hard_delete(db, patient)
    return None


@router.get(
    "/{patient_id}/episodes",
    response_model=List[EpisodeWithTeamAndDoctor],
    status_code=status.HTTP_200_OK,
)
async def list_patient_episodes(
    patient_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current: Annotated[User, Depends(get_current_user)] = None,
):
    patient = await PatientRepository.get_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    episodes = await EpisodeRepository.list_by_patient_id(db, patient_id)

    out: list[EpisodeWithTeamAndDoctor] = []
    for ep in episodes:
        item = EpisodeWithTeamAndDoctor.model_validate(ep)

        # doctores asignados (episode_user -> relación Episode.team_users: List[User])
        team_users = getattr(ep, "team_users", []) or []
        item.assigned_doctors = [UserOut.model_validate(u) for u in team_users]

        # doctores validadores (Episode.validated_by: List[UserEpisodeValidation] -> .user)
        validations = getattr(ep, "validated_by", []) or []
        item.validator_doctors = [
            UserOut.model_validate(v.user)
            for v in validations
            if getattr(v, "user", None)
        ]

        out.append(item)

    return out
