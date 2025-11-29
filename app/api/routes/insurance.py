from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.databases.postgresql.db import get_db
from app.databases.postgresql.models import User
from app.schemas.episode import EpisodeOut
from app.schemas.insurance import InsuranceReviewCreate, InsuranceReviewResponse
from app.services.auth_service import get_current_user, require_admin
from app.services.insurance_service import InsuranceService

router = APIRouter(prefix="/insurance", tags=["insurance"])


@router.post(
    "/review", response_model=InsuranceReviewResponse, status_code=status.HTTP_200_OK
)
async def review_episode(
    payload: InsuranceReviewCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
):
    """
    Create or update an insurance review for an episode.
    Only admins can perform this action.
    """
    try:
        review = await InsuranceService.review_episode(
            db,
            episode_id=payload.episode_id,
            is_pertinent=payload.is_pertinent,
        )
        return review
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@router.get("/pending", response_model=List[EpisodeOut], status_code=status.HTTP_200_OK)
async def get_pending_reviews(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
):
    """
    Get episodes that have been discharged but not yet reviewed by insurance.
    Only admins can see this list.
    """
    episodes = await InsuranceService.get_pending_reviews(db)
    return episodes


@router.get(
    "/{episode_id}",
    response_model=InsuranceReviewResponse,
    status_code=status.HTTP_200_OK,
)
async def get_review_status(
    episode_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Get the insurance review status for a specific episode.
    Accessible by any authenticated user (medical staff, admins).
    """
    review = await InsuranceService.get_review_status(db, episode_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )
    return review
