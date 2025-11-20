from typing import List

import pandas as pd
from sklearn.metrics import f1_score


class ModelEvaluator:
    """
    Calcula las métricas de evaluación para un modelo de machine learning clásico.
    """

    def __init__(self):
        self.metric = "f1_score"

    def upload_data(self, data: List[pd.DataFrame], model) -> None:
        """
        Carga los datos de entrenamiento y la versión del modelo.
        """
        self.features_test = data[0]
        self.target_test = data[1]
        self.model = model

    def calculate_metrics(self) -> float:
        """Calcula la métrica F1-Score."""
        y_true = self.target_test
        y_pred = self.model.predict(self.features_test)
        if self.metric == "f1_score":
            return {
                "metric": self.metric,
                "value": round(f1_score(y_true, y_pred, average="weighted"), 2),
            }

    def evaluate_model(self, data: List[pd.DataFrame], model) -> None:
        """Ejecuta el proceso de evaluación del modelo."""
        self.upload_data(data, model)
        metric = self.calculate_metrics()
        self.print_successful_operation(metric)
        return metric

    def print_successful_operation(self, metric) -> None:
        """Imprime mensaje de exito"""
        print(f"✅ Modelo evaluado: {metric}")
