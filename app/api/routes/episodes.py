from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.databases.postgresql.db import get_db
from app.databases.postgresql.models import User
from app.repositories.episode import EpisodeRepository
from app.schemas.episode import (
    EpisodeCreate,
    EpisodeOut,
    EpisodePage,
    EpisodePageMeta,
    EpisodeUpdate,
)
from app.schemas.episode_assigned_out import EpisodeWithTeam
from app.schemas.episode_validated_out import EpisodeWithDoctor
from app.schemas.user import UserOut
from app.services.auth_service import get_current_user, require_admin, require_medical_role

router = APIRouter(prefix="/episodes", tags=["episodes"])


def _total_pages(total: int, size: int) -> int:
    return (total + size - 1) // size if size else 1


# CREATE (cualquier rol médico: doctor / chief / admin)
@router.post("/", response_model=EpisodeOut, status_code=status.HTTP_201_CREATED)
async def create_episode(
    payload: EpisodeCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_medical_role)],
):
    try:
        ep = await EpisodeRepository.create_with_team(
            db,
            data=payload.model_dump(
                exclude={"diagnostics_ids", "doctors_by_turn"},
                exclude_unset=True,
                by_alias=True,  # permite que la request mande "doctors"
            ),
            diagnostics_ids=payload.diagnostics_ids,
            doctors_by_turn=payload.doctors_by_turn,  # viene de "doctors" (alias)
        )
        return ep
    except IntegrityError:
        raise HTTPException(status_code=409, detail="numero_episodio ya registrado")


# LIST (requiere login)
@router.get("/", response_model=EpisodePage)
async def list_episodes(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = None,
    patient_id: int | None = None,
    _current: Annotated[User, Depends(get_current_user)] = None,
):
    items, total = await EpisodeRepository.list_paginated(
        db, page=page, page_size=page_size, search=search, patient_id=patient_id
    )
    return EpisodePage(
        items=items,
        meta=EpisodePageMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=_total_pages(total, page_size),
        ),
    )


# GET by ID (requiere login)
@router.get("/{episode_id}", response_model=EpisodeOut)
async def get_episode(
    episode_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current: Annotated[User, Depends(get_current_user)] = None,
):
    ep = await EpisodeRepository.get_by_id(db, episode_id)
    if not ep:
        raise HTTPException(status_code=404, detail="Episode not found")
    return ep


# UPDATE (cualquier rol médico: doctor / chief / admin)
@router.patch("/{episode_id}", response_model=EpisodeOut)
async def update_episode(
    episode_id: int,
    payload: EpisodeUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_medical_role)],
):
    ep = await EpisodeRepository.get_by_id(db, episode_id)
    if not ep:
        raise HTTPException(status_code=404, detail="Episode not found")
    try:
        return await EpisodeRepository.update_partial(
            db,
            ep,
            data=payload.model_dump(exclude={"diagnostics_ids"}, exclude_unset=True),
            diagnostics_ids=payload.diagnostics_ids,
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail="numero_episodio ya registrado")


# DELETE (solo admin)
@router.delete("/{episode_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_episode(
    episode_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
):
    ep = await EpisodeRepository.get_by_id(db, episode_id)
    if not ep:
        raise HTTPException(status_code=404, detail="Episode not found")
    await EpisodeRepository.hard_delete(db, ep)
    return None


# ASSIGNED (rol según usuario autenticado)
@router.get("/assigned", response_model=List[EpisodeWithTeam], status_code=status.HTTP_200_OK)
async def list_assigned_episodes(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    - Admin -> todos (equipo completo)
    - Chief -> episodios con al menos un doctor de su 'turn' asignado
    - Doctor -> episodios donde él está asignado
    """
    if getattr(current_user, "is_admin", False):
        episodes = await EpisodeRepository.list_all_with_team(db)
    elif current_user.is_chief_doctor and not current_user.is_admin:
        if not current_user.turn:
            raise HTTPException(status_code=400, detail="Chief doctor has no 'turn' set")
        episodes = await EpisodeRepository.list_by_turn_team(db, current_user.turn)
    elif current_user.is_doctor and not current_user.is_admin:
        episodes = await EpisodeRepository.list_by_user_team(db, current_user.id)
    else:
        raise HTTPException(status_code=403, detail="Role not allowed")

    out: list[EpisodeWithTeam] = []
    for ep in episodes:
        item = EpisodeWithTeam.model_validate(ep)
        team_users = getattr(ep, "team_users", []) or []
        object.__setattr__(item, "assigned_doctors", [UserOut.model_validate(u) for u in team_users])
        out.append(item)

    return out


# VALIDATED (rol según usuario autenticado)
@router.get("/validated", response_model=List[EpisodeWithDoctor], status_code=status.HTTP_200_OK)
async def list_validated_episodes(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    - Admin -> todos
    - Chief -> validados por doctores de su 'turn'
    - Doctor -> donde él es el validador
    """
    if current_user.is_admin:
        episodes = await EpisodeRepository.list_all_with_validators(db)
    elif current_user.is_chief_doctor:
        if not current_user.turn:
            raise HTTPException(status_code=400, detail="Chief doctor has no 'turn' set")
        episodes = await EpisodeRepository.list_by_turn_validations(db, current_user.turn)
    elif current_user.is_doctor:
        episodes = await EpisodeRepository.list_by_doctor_validations(db, current_user.id)
    else:
        raise HTTPException(status_code=403, detail="Role not allowed for this endpoint")

    result: list[EpisodeWithDoctor] = []
    for ep in episodes:
        item = EpisodeWithDoctor.model_validate(ep)
        validator = getattr(ep, "validated_by", []) or []
        object.__setattr__(item, "validator_doctors", [UserOut.model_validate(u) for u in validator])
        result.append(item)

    return result

