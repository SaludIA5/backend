from typing import List, Optional
from sqlalchemy import select, func, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Integer

from app.databases.postgresql.models import ModelVersion


class ModelVersionRepository:
    
    @staticmethod
    async def create(
        db: AsyncSession,
        *,
        version: str,
        stage: str,
        metric: str,
        metric_value: float,
        trained_at,
        active: bool = False,
    ) -> ModelVersion:
        instance = ModelVersion(
            version=version,
            stage=stage,
            metric=metric,
            metric_value=metric_value,
            trained_at=trained_at,
            active=active,
        )
        db.add(instance)
        try:
            await db.commit()
        except IntegrityError as e:
            await db.rollback()
            raise e

        await db.refresh(instance)
        return instance
    
    @staticmethod
    async def get_by_version(db: AsyncSession, version: str) -> Optional[ModelVersion]:
        res = await db.execute(
            select(ModelVersion).where(ModelVersion.version == version)
        )
        return res.scalar_one_or_none()
    @staticmethod
    async def get_active_version_for_stage(db: AsyncSession, stage: str) -> Optional[ModelVersion]:
        stmt = (select(ModelVersion)
        .where(
            ModelVersion.stage == stage,
            ModelVersion.active == True
        )
        .limit(1)
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    @staticmethod
    async def list_all(db: AsyncSession) -> List[ModelVersion]:
        res = await db.execute(select(ModelVersion).order_by(ModelVersion.id.desc()))
        return res.scalars().all()

    @staticmethod
    async def list_by_stage(db: AsyncSession, stage: str) -> List[ModelVersion]:
        res = await db.execute(
            select(ModelVersion)
            .where(ModelVersion.stage == stage)
            .order_by(ModelVersion.id.desc())
        )
        return res.scalars().all()

    @staticmethod
    async def list_prod(db: AsyncSession) -> List[ModelVersion]:
        return await ModelVersionRepository.list_by_stage(db, "prod")

    @staticmethod
    async def list_dev(db: AsyncSession) -> List[ModelVersion]:
        return await ModelVersionRepository.list_by_stage(db, "dev")

    @staticmethod
    async def get_latest_version_for_stage(
        db: AsyncSession, stage: str
    ) -> Optional[ModelVersion]:

        stmt = (
            select(ModelVersion)
            .where(ModelVersion.stage == stage)
            .order_by(
                func.cast(
                    func.split_part(ModelVersion.version, "_v", 2), 
                    Integer
                ).desc()
            )
            .limit(1)
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    @staticmethod
    async def update_partial(
        db: AsyncSession,
        instance: ModelVersion,
        *,
        metric: Optional[str] = None,
        metric_value: Optional[float] = None,
        trained_at=None,
        active: Optional[bool] = None,
        stage: Optional[str] = None,
    ) -> ModelVersion:

        if metric is not None:
            instance.metric = metric
        if metric_value is not None:
            instance.metric_value = metric_value
        if trained_at is not None:
            instance.trained_at = trained_at
        if active is not None:
            instance.active = active
        if stage is not None:
            instance.stage = stage

        try:
            await db.commit()
        except IntegrityError as e:
            await db.rollback()
            raise e

        await db.refresh(instance)
        return instance

    @staticmethod
    async def delete_by_version(db: AsyncSession, version: str) -> None:

        instance = await ModelVersionRepository.get_by_version(db, version)
        if not instance:
            return

        stage = instance.stage
        was_active = instance.active

        await db.execute(delete(ModelVersion).where(ModelVersion.version == version))
        await db.commit()

        if not was_active:
            return

        remaining = await ModelVersionRepository.list_by_stage(db, stage)

        if len(remaining) < 1:
            return

        best = sorted(remaining, key=lambda mv: (mv.metric_value, mv.trained_at), reverse=True)[0]
        for mv in remaining:
            mv.active = (mv.id == best.id)

        await db.commit()

    @staticmethod
    async def delete_by_stage(db: AsyncSession, stage: str) -> None:
        await db.execute(delete(ModelVersion).where(ModelVersion.stage == stage))
        await db.commit()

    @staticmethod
    async def delete_prod(db: AsyncSession) -> None:
        await ModelVersionRepository.delete_by_stage(db, "prod")

    @staticmethod
    async def delete_dev(db: AsyncSession) -> None:
        await ModelVersionRepository.delete_by_stage(db, "dev")
