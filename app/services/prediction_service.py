"""Prediction service for ML model inference."""

from typing import Literal

from fastapi import HTTPException, status
from saluai5_ml import predict_rf, predict_xgb

from app.databases.postgresql.models import User


class PredictionService:
    """Service for episode pertinence prediction using ML models."""

    @staticmethod
    def predict_episode_pertinence(
        episode_data: dict,
        model_type: Literal["random_forest", "xgboost"] = "random_forest",
        current_user: User | None = None,
    ) -> dict:
        """
        Predict if an episode is PERTINENTE or NO PERTINENTE.

        Args:
            episode_data: Dictionary containing episode features
            model_type: Type of model to use ('random_forest' or 'xgboost')

        Returns:
            dict: {
                'prediction': int (0 or 1),
                'probability': float (0.0 to 1.0),
                'label': str ('NO PERTINENTE' or 'PERTINENTE'),
                'model': str (model name used)
            }
        """
        if current_user is None or not (
            getattr(current_user, "is_doctor", False)
            or getattr(current_user, "is_chief_doctor", False)
            or getattr(current_user, "is_admin", False)
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Medical role required to perform predictions",
            )
        # Select predictor based on model type
        if model_type == "random_forest":
            result = predict_rf(episode_data)
        elif model_type == "xgboost":
            result = predict_xgb(episode_data)
        else:
            raise ValueError(f"Invalid model_type: {model_type}.'")

        # Enhance result with label and model info
        result["label"] = "PERTINENTE" if result["prediction"] == 1 else "NO PERTINENTE"
        result["model"] = model_type

        return result
