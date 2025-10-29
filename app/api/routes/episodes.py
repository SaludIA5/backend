from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.databases.postgresql.db import get_db
from app.databases.postgresql.models import User
from app.repositories.episode import EpisodeRepository
from app.repositories.user import UserRepository
from app.repositories.user_episode_validation import UserEpisodeValidationRepository
from app.schemas.episode import (
    EpisodeCreate,
    EpisodeOut,
    EpisodeOutWithPatient,
    EpisodePage,
    EpisodePageMeta,
    EpisodeUpdate,
)
from app.schemas.episode_assigned_out import EpisodeWithTeam
from app.schemas.episode_validated_out import EpisodeWithDoctor
from app.schemas.user import UserOut
from app.schemas.validation import ValidateEpisodeRequest
from app.services.auth_service import (
    get_current_user,
    require_admin,
    require_medical_role,
)

router = APIRouter(prefix="/episodes", tags=["episodes"])


def _total_pages(total: int, size: int) -> int:
    return (total + size - 1) // size if size else 1


# ASSIGNED (rol según usuario autenticado)
@router.get(
    "/assigned", response_model=List[EpisodeWithTeam], status_code=status.HTTP_200_OK
)
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
            raise HTTPException(
                status_code=400, detail="Chief doctor has no 'turn' set"
            )
        episodes = await EpisodeRepository.list_by_turn_team(db, current_user.turn)
    elif current_user.is_doctor and not current_user.is_admin:
        episodes = await EpisodeRepository.list_by_user_team(db, current_user.id)
    else:
        raise HTTPException(status_code=403, detail="Role not allowed")

    out: list[EpisodeWithTeam] = []
    for ep in episodes:
        item = EpisodeWithTeam.model_validate(ep)
        team_users = getattr(ep, "team_users", []) or []
        object.__setattr__(
            item, "assigned_doctors", [UserOut.model_validate(u) for u in team_users]
        )
        patient = getattr(ep, "patient", None)
        if patient:
            object.__setattr__(item, "patient_name", getattr(patient, "name", None))
            object.__setattr__(item, "patient_rut", getattr(patient, "rut", None))
            object.__setattr__(item, "patient_age", getattr(patient, "age", None))
        out.append(item)

    return out


# CREATE (cualquier rol médico: doctor / chief / admin)
@router.post(
    "/", response_model=EpisodeOutWithPatient, status_code=status.HTTP_201_CREATED
)
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
        item = EpisodeOutWithPatient.model_validate(ep)
        patient = getattr(ep, "patient", None)
        if patient:
            object.__setattr__(item, "patient_name", getattr(patient, "name", None))
            object.__setattr__(item, "patient_rut", getattr(patient, "rut", None))
        return item
    except IntegrityError:
        raise HTTPException(status_code=409, detail="numero_episodio ya registrado")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


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


@router.get("/status/{patient_id}", response_model=dict)
async def get_patient_episodes(
    patient_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    episodes = await EpisodeRepository.get_by_patient_id(db, patient_id)
    if not episodes:
        raise HTTPException(
            status_code=404, detail="No episodes found for this patient"
        )

    open_episodes = [ep for ep in episodes if ep.estado_del_caso != "Cerrado"]
    closed_episodes = [ep for ep in episodes if ep.estado_del_caso == "Cerrado"]

    return {
        "patient_id": patient_id,
        "open_episodes": [
            {
                "id": ep.id,
                "estado_del_caso": ep.estado_del_caso,
                "numero_episodio": ep.numero_episodio,
            }
            for ep in open_episodes
        ],
        "closed_episodes": [
            {
                "id": ep.id,
                "estado_del_caso": ep.estado_del_caso,
                "numero_episodio": ep.numero_episodio,
            }
            for ep in closed_episodes
        ],
    }


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


# VALIDAR (solo doctores, jefes de turno y admin), requiere login
@router.post(
    "/{episode_id}/validate", response_model=EpisodeOut, status_code=status.HTTP_200_OK
)
async def validate_episode(
    episode_id: int,
    payload: ValidateEpisodeRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ep = await EpisodeRepository.get_by_id(db, episode_id)
    if not ep:
        raise HTTPException(status_code=404, detail="Episode not found")

    if not (
        getattr(current_user, "is_admin", False)
        or getattr(current_user, "is_chief_doctor", False)
        or getattr(current_user, "is_doctor", False)
    ):
        raise HTTPException(
            status_code=403, detail="User role not allowed to validate episodes"
        )

    if (
        not getattr(current_user, "is_admin", False)
        and payload.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=403, detail="Cannot validate on behalf of another user"
        )

    doctor = await UserRepository.get_by_id(db, payload.user_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="User not found")
    if not (
        getattr(doctor, "is_admin", False)
        or getattr(doctor, "is_chief_doctor", False)
        or getattr(doctor, "is_doctor", False)
    ):
        raise HTTPException(
            status_code=403, detail="Target user role not allowed to validate episodes"
        )

    existing = await UserEpisodeValidationRepository.get_by_episode_id(db, episode_id)
    if existing:
        raise HTTPException(status_code=409, detail="Episode already validated")

    try:
        ep = await EpisodeRepository.update_partial(
            db,
            ep,
            data={"validacion": payload.decision},
            diagnostics_ids=None,
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Conflict updating episode")

    try:
        await UserEpisodeValidationRepository.create(
            db, user_id=payload.user_id, episode_id=episode_id
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Episode already validated")

    ep = await EpisodeRepository.get_by_id(db, episode_id)
    return ep


# VALIDAR FINAL (solo jefe de turno del doctor que validó inicialmente, tienen mismo turno)
# Requiere login
@router.post(
    "/{episode_id}/chief-validate",
    response_model=EpisodeOut,
    status_code=status.HTTP_200_OK,
)
async def chief_validate_episode(
    episode_id: int,
    payload: ValidateEpisodeRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ep = await EpisodeRepository.get_by_id(db, episode_id)
    if not ep:
        raise HTTPException(status_code=404, detail="Episode not found")

    if not (
        getattr(current_user, "is_admin", False)
        or getattr(current_user, "is_chief_doctor", False)
    ):
        raise HTTPException(
            status_code=403, detail="User is not allowed to perform chief validation"
        )

    if (
        not getattr(current_user, "is_admin", False)
        and payload.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=403, detail="Cannot act on behalf of another user"
        )

    chief = await UserRepository.get_by_id(db, payload.user_id)
    if not chief:
        raise HTTPException(status_code=404, detail="User not found")
    if not getattr(chief, "is_chief_doctor", False):
        raise HTTPException(status_code=403, detail="User is not a chief doctor")

    prev_validation = await UserEpisodeValidationRepository.get_with_user_by_episode_id(
        db, episode_id
    )
    if not prev_validation or not prev_validation.user:
        raise HTTPException(
            status_code=409, detail="Episode is not validated by a doctor yet"
        )

    doctor = prev_validation.user

    if not chief.turn or not getattr(doctor, "turn", None):
        raise HTTPException(
            status_code=400,
            detail="Chief or validating doctor has no 'turn' set",
        )
    if chief.turn != doctor.turn:
        raise HTTPException(
            status_code=403,
            detail="Chief doctor and validating doctor are not in the same turn",
        )

    try:
        ep = await EpisodeRepository.update_partial(
            db,
            ep,
            data={"validacion_jefe_turno": payload.decision},
            diagnostics_ids=None,
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Conflict updating episode")

    ep = await EpisodeRepository.get_by_id(db, episode_id)
    return ep


# VALIDATED (rol según usuario autenticado)
@router.get(
    "/validated", response_model=List[EpisodeWithDoctor], status_code=status.HTTP_200_OK
)
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
            raise HTTPException(
                status_code=400, detail="Chief doctor has no 'turn' set"
            )
        episodes = await EpisodeRepository.list_by_turn_validations(
            db, current_user.turn
        )
    elif current_user.is_doctor:
        episodes = await EpisodeRepository.list_by_doctor_validations(
            db, current_user.id
        )
    else:
        raise HTTPException(
            status_code=403, detail="Role not allowed for this endpoint"
        )

    result: list[EpisodeWithDoctor] = []
    for ep in episodes:
        item = EpisodeWithDoctor.model_validate(ep)
        validator = getattr(ep, "validated_by", []) or []
        object.__setattr__(
            item, "validator_doctors", [UserOut.model_validate(u) for u in validator]
        )
        result.append(item)

    return result
