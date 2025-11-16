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
from ml_package.saluai5_ml.training_pipeline.versioner import ModelVersioner

class TrainingOrchestrator:
    """
    Coordina el pipeline de entrenamiento completo.
    """

    def __init__(self, stage, config=None):
        self.stage = stage
        self.config = config
        self.cleaner = DataCleaner()
        self.encoder = DataEncoder(self.stage)
        self.splitter = DataSplitter(train_size=0.8)
        self.trainer = ModelTrainer(self.stage, self.config)
        self.evaluator = ModelEvaluator()
        self.versioner = ModelVersioner(self.stage)

    async def run(self, session):
        """Ejecuta el flujo completo de entrenamiento."""

        # Ingesta de datos
        new_version_label = await self.versioner.generate_new_version_label(session)
        self.loader = DataLoader(session)
        data = await self.loader.fetch_all_episodes_df()

        # Preprocesamiento
        data = self.cleaner.run_preprocessing(data)

        # División de datos para entrenamiento y prueba
        X_train, X_test, y_train, y_test = self.splitter.build_train_test_data(data)

        # Codificación de datos
        X_train, X_test = self.encoder.encode([X_train, X_test], new_version_label)

        # Entrenamiento
        model = self.trainer.train_model([X_train, y_train], new_version_label)

        # Evaluación
        model_metric = self.evaluator.evaluate_model([X_test, y_test], model)

        # Registro de versiones
        new_model_version = await self.versioner.save_model_metrics(
            session, model_metric, new_version_label
        )

        print(f"✅ Nueva versión de modelo registrada: {new_model_version.version} ({new_model_version.trained_at})")
        return new_model_version
