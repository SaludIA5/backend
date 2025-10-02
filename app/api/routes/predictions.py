"""Prediction endpoints for ML models."""

from fastapi import APIRouter, HTTPException, status

from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.prediction_service import PredictionService

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.post("/", response_model=PredictionResponse, status_code=status.HTTP_200_OK)
async def predict_episode_pertinence(payload: PredictionRequest):
    """
    Predict if an episode is PERTINENTE or NO PERTINENTE using ML models.

    This endpoint uses trained ML models (Random Forest or XGBoost) to predict
    the pertinence classification of a medical episode based on patient data,
    vital signs, procedures, and laboratory results.

    Missing values will be automatically filled with representative values
    (means for numerical, modes for categorical).

    Args:
        payload: Episode data and model selection

    Returns:
        PredictionResponse with prediction, probability, label and model used

    Raises:
        HTTPException: If prediction fails or invalid model type
    """
    try:
        # Extract episode data (excluding model_type)
        episode_data = payload.model_dump(exclude={"model_type"}, exclude_none=True)

        # Make prediction
        result = PredictionService.predict_episode_pertinence(
            episode_data=episode_data, model_type=payload.model_type
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al realizar la predicción: {str(e)}",
        )
