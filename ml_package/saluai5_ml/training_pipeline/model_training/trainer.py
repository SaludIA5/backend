from pathlib import Path
from typing import List

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier


class ModelTrainer:
    """
    Se encarga de entrenar un modelo de machine learning clásico en base a
    los datos preprocesados.
    """

    def __init__(self, config=None):
        self.config = config
        self.model_name = "random_forest"

    def upload_data(self, data: List[pd.DataFrame], version: str) -> None:
        """
        Carga los datos de entrenamiento y la versión del modelo.
        """
        self.features_train = data[0]
        self.target_train = data[1]
        self.label_version = version

    def models_factory(self):
        """Factory para crear modelos de ML clásicos."""
        if self.config is None:
            return RandomForestClassifier(
                n_estimators=100, max_depth=10, bootstrap=True, random_state=23
            )
        return RandomForestClassifier(**self.config)

    def train_model(self, data: List[pd.DataFrame], version: str) -> None:
        """Entrena el modelo de machine learning clásico."""
        self.upload_data(data, version)
        model = self.models_factory()
        model.fit(self.features_train, self.target_train)
        self.model_serializer(model)
        self.print_successful_operation()
        return model

    def get_base_directory_package(self) -> Path:
        """
        Obtiene el directorio base del proyecto.
        """
        return Path(__file__).resolve().parent.parent.parent

    def get_versioning_label(self) -> None:
        """
        Crea una etiqueta de versión para el modelo de ML.
        """
        return f"{self.label_version}.pkl"

    def model_serializer(self, model) -> None:
        """
        Serializa el modelo en un archivo pkl.
        """
        file_name = self.get_versioning_label()
        base_path = self.get_base_directory_package()
        file_path = base_path / "models_repository" / file_name
        joblib.dump(model, file_path)

    def print_successful_operation(self) -> None:
        """Imprime mensaje de exito"""
        print(f"✅ Modelo {self.model_name} entrenado y serializado exitosamente.")
