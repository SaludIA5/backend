from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.databases.postgresql.db import get_db
from app.databases.postgresql.models import User
from app.schemas.doctor_summary import DoctorSummaryCreate, DoctorSummaryRead
from app.repositories.doctor_summary import DoctorSummaryRepository
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/doctor-summaries", tags=["doctor-summaries"])


# CREATE (requiere login)
@router.post(
    "",
    response_model=DoctorSummaryRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_doctor_summary(
    payload: DoctorSummaryCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    # user_id SIEMPRE es el del usuario logeado
    summary = await DoctorSummaryRepository.create(
        db,
        episode_id=payload.episode_id,
        user_id=current_user.id,
        comment=payload.comment,
    )
    return summary


# GET por ID (requiere login)
@router.get(
    "/{summary_id}",
    response_model=DoctorSummaryRead,
    status_code=status.HTTP_200_OK,
)
async def get_doctor_summary(
    summary_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current: Annotated[User, Depends(get_current_user)],
):
    summary = await DoctorSummaryRepository.get_by_id(db, summary_id)
    if not summary:
        raise HTTPException(status_code=404, detail="doctor_summary no encontrado")
    return summary


# LIST (requiere login)
@router.get(
    "",
    response_model=List[DoctorSummaryRead],
    status_code=status.HTTP_200_OK,
)
async def list_doctor_summaries(
    db: Annotated[AsyncSession, Depends(get_db)],
    _current: Annotated[User, Depends(get_current_user)],
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    items = await DoctorSummaryRepository.list_all(db, offset=offset, limit=limit)
    return items


# LIST por episodio (requiere login)
@router.get(
    "/by-episode/{episode_id}",
    response_model=List[DoctorSummaryRead],
    status_code=status.HTTP_200_OK,
)
async def list_doctor_summaries_by_episode(
    episode_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current: Annotated[User, Depends(get_current_user)],
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    items = await DoctorSummaryRepository.list_by_episode(
        db, episode_id=episode_id, offset=offset, limit=limit
    )
    return items

