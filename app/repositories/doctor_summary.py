from typing import Sequence, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.databases.postgresql.models.doctor_summary import DoctorSummary

class DoctorSummaryRepository:
    @staticmethod
    async def create(
        db: AsyncSession,
        *,
        episode_id: int,
        user_id: int,
        comment: str,
    ) -> DoctorSummary:
        instance = DoctorSummary(
            episode_id=episode_id,
            user_id=user_id,
            comment=comment,
        )
        db.add(instance)
        await db.commit()
        await db.refresh(instance)
        return instance

    @staticmethod
    async def get_by_id(db: AsyncSession, summary_id: int) -> Optional[DoctorSummary]:
        res = await db.execute(
            select(DoctorSummary).where(DoctorSummary.id == summary_id)
        )
        return res.scalar_one_or_none()

    @staticmethod
    async def list_all(
        db: AsyncSession, *, offset: int = 0, limit: int = 100
    ) -> Sequence[DoctorSummary]:
        res = await db.execute(
            select(DoctorSummary)
            .order_by(DoctorSummary.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return res.scalars().all()

    @staticmethod
    async def list_by_episode(
        db: AsyncSession, episode_id: int, *, offset: int = 0, limit: int = 100
    ) -> Sequence[DoctorSummary]:
        res = await db.execute(
            select(DoctorSummary)
            .where(DoctorSummary.episode_id == episode_id)
            .order_by(DoctorSummary.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return res.scalars().all()
