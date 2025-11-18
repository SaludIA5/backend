"""Inference service for ML model inference."""

from fastapi import HTTPException, status
from app.databases.postgresql.db import get_async_session_local

from ml_package.saluai5_ml.inference_pipeline.inference_engine import InferenceEngine
from app.databases.postgresql.models import User


class InferenceService:
    """
    Service that wraps the inference pipeline providing proper DB session handling
    and role validation.
    """

    @staticmethod
    def _validate_user_permissions(user: User | None):
        """Ensures the user has medical privileges to run predictions."""
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User authentication required",
            )

        if not (
            getattr(user, "is_doctor", False)
            or getattr(user, "is_chief_doctor", False)
            or getattr(user, "is_admin", False)
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Medical role required to perform predictions",
            )

    @staticmethod
    async def predict_episode_pertinence(
        episode_data: dict,
        current_user: User | None = None,
        stage: str = "prod",
    ) -> dict:
        """
        Predict if an episode is PERTINENTE or NO PERTINENTE.

        Args:
            episode_data: Dictionary with episode features.
            stage: Inference stage ("prod" by default). Useful for tests.

        Returns:
            dict: {
                'prediction': int,
                'probability': float,
                'label': str,
            }
        """
        # Validate permissions
        InferenceService._validate_user_permissions(current_user)

        # Prepare inference engine
        engine = InferenceEngine(episode_data=episode_data, stage=stage)

        # Create DB session as FastAPI would
        SessionLocal = get_async_session_local()

        async with SessionLocal() as session:
            try:
                result = await engine.run(session)
                return result
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error during inference: {str(e)}",
                )