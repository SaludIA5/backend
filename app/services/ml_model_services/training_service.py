import asyncio
from app.databases.postgresql.db import get_async_session_local
from ml_package.saluai5_ml.training_pipeline.orchestrator import TrainingOrchestrator


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

if __name__ == "__main__":
    import sys

    stage = sys.argv[1] if len(sys.argv) > 1 else "dev"

    service = TrainingService(stage=stage)
    asyncio.run(service.run_training())