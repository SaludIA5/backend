"""
SALUAI5 ML Package

Paquete de Machine Learning para predicción de pertinencia de episodios médicos.
"""

__version__ = "0.1.0"

from saluai5_ml.models.random_forest.inference import make_prediction as predict_rf
from saluai5_ml.models.xgboost.inference import make_prediction as predict_xgb
from saluai5_ml.training_pipeline.orchestrator import TrainingOrchestrator as training_orchestrator

__all__ = [
    "predict_rf",
    "predict_xgb",
    "training_orchestrator",
]
