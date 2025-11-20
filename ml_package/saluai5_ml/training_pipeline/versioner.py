from datetime import date
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.model_versions import ModelVersionRepository


class ModelVersioner:
    def __init__(self, stage: str):
        self.stage = stage

    async def get_last_version(self, db: AsyncSession):
        """Retorna el último ModelVersion para un stage."""
        last_version = await ModelVersionRepository.get_latest_version_for_stage(db, self.stage)
        return last_version

    async def generate_new_version_label(self, db: AsyncSession) -> str:
        """Genera prod_v{i} o dev_v{i} según corresponda."""
        last = await self.get_last_version(db)

        if last is None:
            return f"{self.stage}_v1"

        _, version_number = last.version.split("_v")
        next_version = int(version_number) + 1
        return f"{self.stage}_v{next_version}"

    async def save_model_metrics(
        self, db: AsyncSession, metric_info: Dict[str, Any], version: str
    ):
        """Inserta una nueva fila en model_versions."""
        versions = await ModelVersionRepository.list_by_stage(db, self.stage)
        if not versions:
            instance = await ModelVersionRepository.create(
				db,
				version=version,
				stage=self.stage,
				metric=metric_info["metric"],
				metric_value=float(metric_info["value"]),
				trained_at=date.today(),
				active=True,
            )
            return instance

        else:
            
            active_instance = await ModelVersionRepository.get_active_version_for_stage(db, self.stage)
            if active_instance is None:
                instance = await ModelVersionRepository.create(
                    db,
                    version=version,
                    stage=self.stage,
                    metric=metric_info["metric"],
                    metric_value=float(metric_info["value"]),
                    trained_at=date.today(),
                    active=True,
                )
                return instance
            
            if float(metric_info["value"]) >= active_instance.metric_value:
                await ModelVersionRepository.update_partial(db, active_instance, active=False)
                instance = await ModelVersionRepository.create(
					db,
					version=version,
					stage=self.stage,
					metric=metric_info["metric"],
					metric_value=float(metric_info["value"]),
					trained_at=date.today(),
					active=True,
				)
                return instance
            
            else:
                instance = await ModelVersionRepository.create(
					db,
					version=version,
					stage=self.stage,
					metric=metric_info["metric"],
					metric_value=float(metric_info["value"]),
					trained_at=date.today(),
					active=False,
				)
                return instance