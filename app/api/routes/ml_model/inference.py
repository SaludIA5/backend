from fastapi import APIRouter
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.databases.postgresql.db import get_db
from app.databases.postgresql.models import Episode, User
# from app.databases.postgresql.models import User
from app.schemas.ml_model.inference import InferenceRequest, InferenceResponse
from app.services.auth_service import require_medical_role
from app.services.ml_model_services.inference_service import InferenceService

router = APIRouter(prefix="/inference",tags=["ML Model - Inference"])

@router.post("/", response_model=InferenceResponse, status_code=status.HTTP_200_OK)
async def predict_episode_pertinence(
    payload: InferenceRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_medical_role)],
):
    """
    Predict if an episode is PERTINENTE or NO PERTINENTE using ML models.

    This endpoint uses trained ML model to predict
    the pertinence classification of a medical episode based on patient data,
    vital signs, procedures, and laboratory results.

    Missing values will be automatically filled with representative values
    (means for numerical, modes for categorical).

    Args:
        payload: Episode data and model selection

    Returns:
        PredictionResponse with prediction, probability, label

    Raises:
        HTTPException: If prediction fails or invalid model type
    """
    try:

        episode_data = payload.model_dump(exclude={"id_episodio", "stage", "model_type", "numero_episodio"})
        result = await InferenceService.predict_episode_pertinence(
            episode_data=episode_data,
            current_user=current_user,
            stage=payload.stage
        )

        episode_id = payload.id_episodio
        if episode_id:

            res = await db.execute(select(Episode).where(Episode.id == episode_id))
            ep = res.scalar_one_or_none()

            if ep:

                try:
                    await db.execute(
                        update(Episode)
                        .where(Episode.id == ep.id)
                        .values(recomendacion_modelo=result.get("label"))
                    )
                    await db.commit()
                except:
                    await db.rollback()
                    raise
        print(result)
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al realizar la predicción: {str(e)}",
        )