from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.databases.postgresql.models import Episode, InsuranceReview
from app.repositories.insurance_repository import InsuranceRepository


class InsuranceService:
    @staticmethod
    async def review_episode(
        db: AsyncSession,
        episode_id: int,
        is_pertinent: Optional[bool],
    ) -> InsuranceReview:
        exists = await db.execute(select(Episode.id).where(Episode.id == episode_id))
        if exists.scalar_one_or_none() is None:
            raise ValueError(f"Episode with id {episode_id} not found")
        return await InsuranceRepository.create_or_update(db, episode_id, is_pertinent)

    @staticmethod
    async def get_pending_reviews(db: AsyncSession) -> List[Episode]:
        return await InsuranceRepository.get_pending_episodes(db)

    @staticmethod
    async def get_review_status(
        db: AsyncSession, episode_id: int
    ) -> Optional[InsuranceReview]:
        return await InsuranceRepository.get_by_episode_id(db, episode_id)
