from ml_package.saluai5_ml.inference_pipeline.data_ingestion.loader import DataLoader
from ml_package.saluai5_ml.inference_pipeline.data_preparation.cleaner import DataCleaner
from ml_package.saluai5_ml.inference_pipeline.data_preparation.encoder import DataEncoder
from ml_package.saluai5_ml.inference_pipeline.artifacts.loader import ArtifactsLoader

from app.repositories.model_versions import ModelVersionRepository

class InferenceEngine:
    """
    Coordina el pipeline de inferencia.
    """

    def __init__(self, episode_data, stage="prod"):
        self.episode_data = episode_data
        self.stage = stage
        self.cleaner = DataCleaner()
        self.encoder = DataEncoder(self.stage)

    async def run(self, session):
        """Ejecuta el flujo completo de inferencia."""
        # Obtener versión activa del modelo
        active_version = await self.get_active_version(session)

        # Ingesta de datos
        self.data_loader = DataLoader(session)
        data = await self.loader.fetch_all_episodes_df()

        # Ingesta de artefactos
        self.artifacts_loader = ArtifactsLoader(version = active_version)
        artifacts = await self.artifacts_loader.run()

        # Preprocesamiento
        episode_data_cleaned = self.cleaner.run_preprocessing([data, self.episode_data], artifacts["multilabel_classes"])

        # Codificación de datos
        #X_train, X_test = self.encoder.encode([X_train, X_test], new_version_label)
    
    async def get_active_version(self, session):
        """Obtiene la versión activa del modelo para el stage configurado."""

        instance = await ModelVersionRepository.get_active_version_for_stage(session, stage=self.stage)
        return str(instance.version)