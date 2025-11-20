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
        self.encoder = DataEncoder()

    async def run(self, session):
        """Ejecuta el flujo completo de inferencia."""

        # Primero se checkea si hay versiones entrenadas
        await self.check_trained_versions_stage(session)

        # Obtener versión activa del modelo
        active_version = await self.get_active_version(session)

        # Ingesta de datos
        self.data_loader = DataLoader(session)
        data = await self.data_loader.fetch_all_episodes_df()

        # Ingesta de artefactos
        self.artifacts_loader = ArtifactsLoader(version = active_version)
        artifacts = self.artifacts_loader.run()

        # Preprocesamiento
        episode_data_cleaned = self.cleaner.run_preprocessing([data, self.episode_data], artifacts["multilabel_classes"])

        # Codificación de datos
        episode_data_encoded = self.encoder.encode(episode_data_cleaned, artifacts)

        # Ejecutar predicción y construir payload
        print(active_version)
        payload_prediction = self.predict_and_build_payload(artifacts["model"], episode_data_encoded)
        return payload_prediction
    
    async def check_trained_versions_stage(self, session):
        """Checkea si hay versiones entrenadas para cierta stage"""

        instances = await ModelVersionRepository.list_by_stage(session, stage=self.stage)
        if not instances:
            raise ValueError(
                f"No existen versiones entrenadas del modelo para el stage '{self.stage}'. "
                "Entrena un modelo antes de hacer inferencia."
            )
    
    async def get_active_version(self, session):
        """Obtiene la versión activa del modelo para el stage configurado."""

        instance = await ModelVersionRepository.get_active_version_for_stage(session, stage=self.stage)
        if instance is None:
            raise ValueError(
                f"No existe una versión activa del modelo para el stage '{self.stage}'. "
                "Activa una versión antes de hacer inferencia."
            )
        return str(instance.version)
    
    def predict_and_build_payload(self, model, df):
        """
        Ejecuta la predicción del modelo y construye el payload ordenado.
        Soporta modelos con clases string o numéricas.
        """

        # Predicción
        prediction = model.predict(df)[0]
        probabilities = model.predict_proba(df)[0]

        # Mapeo entre label y su índice basado en clases del modelo
        class_names = list(model.classes_)
        prediction_index = class_names.index(prediction)

        # Probabilidad correspondiente a la clase predicha
        prediction_probability = round(float(probabilities[prediction_index]), 2)

        # Payload final
        return {
            "prediction": prediction_index,
            "label": prediction,
            "probability": prediction_probability
        }

if __name__ == "__main__":
    import asyncio
    from app.databases.postgresql.db import get_async_session_local

    async def _run_manual_inference():
        # Datos de prueba
        episode_data = {
                "id_episodio": 0,
                "stage": "prod",
                "diagnostics": ["A"],
                "antecedentes_cardiaco": True,
                "antecedentes_diabetes": True,
                "antecedentes_hipertension": None,
                "creatinina": "50",
                "fio2": 0.5,
                "fio2_ge_50": None,
                "frecuencia_cardiaca": 150,
                "frecuencia_respiratoria": 150,
                "glasgow_score": 15,
                "hemoglobina": None,
                "nitrogeno_ureico": None,
                "pcr": 20,
                "potasio": 50,
                "presion_diastolica": 20,
                "presion_media": 100,
                "presion_sistolica": 100,
                "saturacion_o2": 0.5,
                "sodio": 100,
                "temperatura_c": 35,
                "tipo": "SIN ALERTA",
                "tipo_alerta_ugcc": "SIN ALERTA",
                "tipo_cama": "Básica",
                "triage": 3,
                "ventilacion_mecanica": True,
                "cirugia_realizada": None,
                "cirugia_mismo_dia_ingreso": None,
                "hemodinamia": None,
                "hemodinamia_mismo_dia_ingreso": None,
                "endoscopia": True,
                "endoscopia_mismo_dia_ingreso": True,
                "dialisis": True,
                "trombolisis": False,
                "trombolisis_mismo_dia_ingreso": None,
                "dreo": None,
                "troponinas_alteradas": True,
                "ecg_alterado": True,
                "rnm_protocolo_stroke": True,
                "dva": None,
                "transfusiones": None,
                "compromiso_conciencia": True
            }

        stage = "prod"

        # Instanciar el engine
        engine = InferenceEngine(
            episode_data=episode_data,
            stage=stage
        )

        # Crear sesión como FastAPI lo haría
        SessionLocal = get_async_session_local()

        async with SessionLocal() as session:
            try:
                result = await engine.run(session)
                print("Resultado de inferencia:", result)

            except Exception as e:
                print(f"Error durante inferencia: {str(e)}")

    asyncio.run(_run_manual_inference())