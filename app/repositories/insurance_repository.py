from typing import List, Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.databases.postgresql.models import Episode, InsuranceReview


class InsuranceRepository:
    @staticmethod
    async def create_or_update(
        db: AsyncSession,
        episode_id: int,
        is_pertinent: Optional[bool],
    ) -> InsuranceReview:
        # Check if exists
        stmt = select(InsuranceReview).where(InsuranceReview.episode_id == episode_id)
        result = await db.execute(stmt)
        review = result.scalar_one_or_none()

        if review:
            review.is_pertinent = is_pertinent
        else:
            review = InsuranceReview(
                episode_id=episode_id,
                is_pertinent=is_pertinent,
            )
            db.add(review)

        await db.commit()
        await db.refresh(review)
        return review

    @staticmethod
    async def get_by_episode_id(
        db: AsyncSession, episode_id: int
    ) -> Optional[InsuranceReview]:
        stmt = select(InsuranceReview).where(InsuranceReview.episode_id == episode_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_pending_episodes(db: AsyncSession) -> List[Episode]:
        # Episodes that have fecha_alta (discharged) but NO InsuranceReview
        stmt = (
            select(Episode)
            .outerjoin(InsuranceReview, Episode.id == InsuranceReview.episode_id)
            .where(
                Episode.fecha_alta.is_not(None),  # Discharged
                or_(
                    InsuranceReview.id.is_(None),
                    InsuranceReview.is_pertinent.is_(None),
                ),
            )
            .options(
                selectinload(Episode.diagnostics),
                selectinload(Episode.patient),
            )
            .order_by(Episode.fecha_alta.desc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()
