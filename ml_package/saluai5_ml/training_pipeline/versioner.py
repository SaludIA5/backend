# from datetime import date
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.repositories.model_versions import ModelVersionRepository


# class ModelVersioner:
#     def __init__(self, stage: str):
#         self.stage = stage

#     async def get_last_version(self, db: AsyncSession):
#         """Retorna el último ModelVersion para un stage."""
#         last_version = await ModelVersionRepository.get_latest_version_for_stage(db, self.stage)
#         return last_version

#     async def generate_new_version_label(self, db: AsyncSession) -> str:
#         """Genera prod_v{i} o dev_v{i} según corresponda."""
#         last = await self.get_last_version(db)

#         if last is None:
#             return f"{self.stage}_v1"

#         _, version_number = last.version.split("_v")
#         next_version = int(version_number) + 1
#         return f"{self.stage}_v{next_version}"

#     async def save_model_metrics(
#         self, db: AsyncSession, metrics: float, version: str
#     ):
#         """Inserta una nueva fila en model_versions."""

#         instance = await ModelVersionRepository.create(
#             db,
#             version=version,
#             stage=self.stage,
#             metric="f1_score",
#             metric_value=float(metrics),
#             trained_at=date.today(),
#             active=True,
#         )
#         return instance