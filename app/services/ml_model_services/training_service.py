import asyncio
import logging

from app.databases.postgresql.db import get_async_session_local
from ml_package.saluai5_ml.training_pipeline.orchestrator import TrainingOrchestrator

logger = logging.getLogger("uvicorn.error")


class TrainingService:
    """
    Wrapper service to run ML training using a proper DB session.
    """

    def __init__(self, stage: str = "dev", config=None):
        self.stage = stage
        self.config = config
        self.orchestrator = TrainingOrchestrator(stage=self.stage, config=self.config)

    async def run_training(self):
        """
        Runs the training pipeline using a DB session created the same way FastAPI does.
        """
        SessionLocal = get_async_session_local()

        async with SessionLocal() as session:
            result = await self.orchestrator.run(session)

        return result

    @staticmethod
    async def execute_background_task(stage: str):
        """
        Método estático para ser llamado por BackgroundTasks.
        Maneja logs y excepciones ya que no hay respuesta HTTP.
        """
        logger.info(
            f"🔄 [BACKGROUND] Iniciando reentrenamiento automático para stage: {stage}"
        )

        try:
            service = TrainingService(stage=stage)
            result = await service.run_training()

            logger.info(
                "[BACKGROUND] Entrenamiento automático finalizado exitosamente."
            )
            logger.info(
                f"📊 Nueva versión: {result.version} | Fecha: {result.trained_at}"
            )

        except Exception as e:
            logger.error(
                f"❌ [BACKGROUND] Falló el pipeline de entrenamiento automático: {str(e)}"
            )


if __name__ == "__main__":
    import sys

    stage = sys.argv[1] if len(sys.argv) > 1 else "dev"

    service = TrainingService(stage=stage)
    asyncio.run(service.run_training())
