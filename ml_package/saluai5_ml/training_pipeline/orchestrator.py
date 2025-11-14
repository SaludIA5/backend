import asyncio
import os
import sys

from app.databases.postgresql.db import get_async_session_local
from ml_package.saluai5_ml.training_pipeline.data_ingestion.loader import DataLoader
from ml_package.saluai5_ml.training_pipeline.data_preparation.cleaner import DataCleaner
from ml_package.saluai5_ml.training_pipeline.data_preparation.encoder import DataEncoder
from ml_package.saluai5_ml.training_pipeline.data_preparation.splitter import (
    DataSplitter,
)
from ml_package.saluai5_ml.training_pipeline.model_training.evaluator import (
    ModelEvaluator,
)
from ml_package.saluai5_ml.training_pipeline.model_training.trainer import ModelTrainer


class TrainingOrchestrator:
    """
    Coordina el pipeline de entrenamiento completo.
    """

    def __init__(self, stage, config=None):
        self.stage = stage
        self.config = config
        self.cleaner = DataCleaner()
        self.encoder = DataEncoder()
        self.splitter = DataSplitter(train_size=0.8)
        self.trainer = ModelTrainer(self.stage, self.config)
        self.evaluator = ModelEvaluator()

    async def run(self):
        """Ejecuta el flujo completo de entrenamiento."""

        # Ingesta de datos
        AsyncSessionLocal = get_async_session_local()
        async with AsyncSessionLocal() as session:
            self.loader = DataLoader(session)
            data = await self.loader.fetch_all_episodes_df()

        # Preprocesamiento
        data = self.cleaner.run_preprocessing(data)

        # División de datos para entrenamiento y prueba
        X_train, X_test, y_train, y_test = self.splitter.build_train_test_data(data)

        # Codificación de datos
        label_version = "v1"
        X_train, X_test = self.encoder.encode([X_train, X_test], label_version)

        # Entrenamiento
        model = self.trainer.train_model([X_train, y_train], label_version)

        # Evaluación
        metrics = self.evaluator.evaluate_model([X_test, y_test], model)
        print(metrics)
        # # Guardar modelo
        # self.trainer.save_model(model)

        # print("✅ Entrenamiento completado con métricas:", metrics)
        # return metrics

    async def get_last_model_version(self):
        """Obtiene la última versión entrenada hasta el momento"""
        await self.loader.close_session()

    async def generate_label_version(self):
        """Genera una nueva etiqueta de versión para el modelo"""
        last_version = await self.get_last_model_version()
        if last_version is None:
            return "v1"
        version_number = int(last_version.strip("v")) + 1
        return f"v{version_number}"

    async def save_model_metrics(self, metrics: float, model_version: str):
        """Se encarga de guardar las métricas del modelo en la base de datos"""
        await self.loader.close_session()


# 👇 Ejecutar manualmente si se corre este archivo directo
if __name__ == "__main__":

    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    sys.path.insert(0, root_path)

    stage = "dev"
    orchestrator = TrainingOrchestrator(stage=stage)

    asyncio.run(orchestrator.run())
