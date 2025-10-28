from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.databases.postgresql.models import UserEpisodeValidation


class UserEpisodeValidationRepository:
    @staticmethod
    async def get_by_episode_id(
        db: AsyncSession, episode_id: int
    ) -> Optional[UserEpisodeValidation]:
        res = await db.execute(
            select(UserEpisodeValidation).where(
                UserEpisodeValidation.episode_id == episode_id
            )
        )
        return res.scalar_one_or_none()

    @staticmethod
    async def get_with_user_by_episode_id(
        db: AsyncSession, episode_id: int
    ) -> Optional[UserEpisodeValidation]:
        res = await db.execute(
            select(UserEpisodeValidation)
            .options(joinedload(UserEpisodeValidation.user))
            .where(UserEpisodeValidation.episode_id == episode_id)
        )
        return res.scalar_one_or_none()

    @staticmethod
    async def create(
        db: AsyncSession, *, user_id: int, episode_id: int
    ) -> UserEpisodeValidation:
        instance = UserEpisodeValidation(user_id=user_id, episode_id=episode_id)
        db.add(instance)
        try:
            await db.commit()
        except IntegrityError as e:
            await db.rollback()
            raise e
        await db.refresh(instance)
        return instance
