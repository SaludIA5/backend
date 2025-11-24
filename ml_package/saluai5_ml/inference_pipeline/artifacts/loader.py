from pathlib import Path
from typing import Dict

import joblib


class ArtifactsLoader:

    def __init__(self, version: str):
        """
        Inicializa Artifacts Loader con la version de los encoders a usar
        """
        self.version = version

    def get_base_directory_package(self) -> Path:
        """
        Obtiene el directorio base del proyecto.
        """
        return Path(__file__).resolve().parent.parent.parent

    def load_data_encoders(self) -> any:
        """
        Carga los encoders de los datos
        """
        try:
            stage = self.version.split("_v")[0]
            base_path = self.get_base_directory_package()
            encoders_path = base_path / "encoders_repository" / stage
            categorical_encoder_path = encoders_path / f"categorical/{self.version}.pkl"
            multilabel_encoder_path = encoders_path / f"multilabel/{self.version}.pkl"
            numerical_encoder_path = encoders_path / f"numerical/{self.version}.pkl"
            categorical_encoder = joblib.load(categorical_encoder_path)
            multilabel_encoder = joblib.load(multilabel_encoder_path)
            numerical_encoder = joblib.load(numerical_encoder_path)
            return (categorical_encoder, multilabel_encoder, numerical_encoder)

        except Exception as e:
            raise FileNotFoundError(
                f"Error crítico del sistema: No se pudieron cargar los artefactos del modelo {self.version}"
                f"(encoders) en la ruta {encoders_path}. Entrena o activa otra version del modelo."
                f"Detalle técnico: {e}"
            ) from e

    def load_ml_model(self) -> any:
        """
        Load the trained model from a file.
        """
        try:
            stage = self.version.split("_v")[0]
            base_path = self.get_base_directory_package()
            model_path = base_path / "models_repository" / stage / f"{self.version}.pkl"
            model = joblib.load(model_path)
            return model

        except Exception as e:
            raise FileNotFoundError(
                f"Error crítico del sistema: No se pudieron cargar los artefactos del modelo {self.version}"
                f"(modelo serializado) en la ruta {model_path}. Entrena o activa otra version del modelo."
                f"Detalle técnico: {e}"
            ) from e

    def get_multilabel_classes(self, multilabel_encoder) -> set:
        """
        Obtiene las clases del encoder multilabel
        """
        return set(multilabel_encoder.classes_)

    def run(self) -> Dict:
        """Retorna los encoders y el modelo en un diccionario."""
        model = self.load_ml_model()
        data_encoders = self.load_data_encoders()
        multilabel_classes = self.get_multilabel_classes(data_encoders[1])
        self.print_successful_operation()
        return {
            "model": model,
            "data_encoders": data_encoders,
            "multilabel_classes": multilabel_classes,
        }

    def print_successful_operation(self) -> None:
        """Imprime mensaje de exito"""
        print(f"✅ Modelo predictivo y encoders cargados: version {self.version}")
