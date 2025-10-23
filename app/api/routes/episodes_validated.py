# app/api/routes/episodes_scope.py
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.databases.postgresql.db import get_db
from app.databases.postgresql.models import User
from app.repositories.episode import EpisodeRepository
from app.schemas.episode_validated_out import EpisodeWithDoctor
from app.schemas.user import UserOut
from app.services.auth_service import get_current_user  # debe existir

router = APIRouter(prefix="/episodes-validated", tags=["episodes"])


@router.get("/", response_model=List[EpisodeWithDoctor], status_code=status.HTTP_200_OK)
async def list_validated_episodes(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    - Admin -> todos los episodios
    - Jefe de turno -> episodios validados por doctores de su mismo turno
    - Doctor -> episodios donde él es el validador
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

    # Construcción de respuesta
    result = []
    for ep in episodes:
        doctor = ep.validated_by.user if getattr(ep, "validated_by", None) else None
        item = EpisodeWithDoctor.model_validate(ep)
        object.__setattr__(item, "doctor", UserOut.model_validate(doctor) if doctor else None)
        result.append(item)

    return result
