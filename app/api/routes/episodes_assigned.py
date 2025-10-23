from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.databases.postgresql.db import get_db
from app.databases.postgresql.models import User
from app.repositories.episode import EpisodeRepository
from app.schemas.episode_assigned_out import EpisodeWithTeam
from app.schemas.user import UserOut
from app.services.auth_service import get_current_user  # el helper que creamos antes

router = APIRouter(prefix="/episodes-assigned", tags=["episodes"])

@router.get("/", response_model=List[EpisodeWithTeam], status_code=status.HTTP_200_OK)
async def list_assigned_episodes(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Devuelve episodios asociados por equipo (episode_user):
    - Admin -> todos los episodios (con equipo completo).
    - Jefe de turno -> episodios con al menos un doctor de su 'turn' asignado.
    - Doctor -> episodios donde él está asignado.
    """
    # Admin
    if getattr(current_user, "is_admin", False):
        episodes = await EpisodeRepository.list_all_with_team(db)

    # Jefe de turno
    elif current_user.is_chief_doctor and not current_user.is_admin:
        if not current_user.turn:
            raise HTTPException(status_code=400, detail="Chief doctor has no 'turn' set")
        episodes = await EpisodeRepository.list_by_turn_team(db, current_user.turn)

    # Doctor
    elif current_user.is_doctor and not current_user.is_admin:
        episodes = await EpisodeRepository.list_by_user_team(db, current_user.id)

    else:
        raise HTTPException(status_code=403, detail="Role not allowed")

    # Mapear a EpisodeWithTeam agregando 'team'
    out: list[EpisodeWithTeam] = []
    for ep in episodes:
        item = EpisodeWithTeam.model_validate(ep)
        # set team
        team_users = getattr(ep, "team_users", []) or []
        object.__setattr__(item, "team", [UserOut.model_validate(u) for u in team_users])
        out.append(item)

    return out
