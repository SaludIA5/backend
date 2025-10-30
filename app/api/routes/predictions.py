"""Prediction endpoints for ML models."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.databases.postgresql.db import get_db
from app.databases.postgresql.models import Episode, User
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.auth_service import require_medical_role
from app.services.prediction_service import PredictionService

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.post("/", response_model=PredictionResponse, status_code=status.HTTP_200_OK)
async def predict_episode_pertinence(
    payload: PredictionRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_medical_role)],
):
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
        episode_data = payload.model_dump(exclude={"model_type", "id_episodio"})
        # print(episode_data)
        # Make prediction
        result = PredictionService.predict_episode_pertinence(
            episode_data=episode_data,
            model_type=payload.model_type,
            current_user=current_user,
        )

        # Se agrega a la columna "recomendacion modelo del respectivo episodio"
        episode_id = payload.id_episodio
        if episode_id:
            try:
                # Buscar el episodio por numero_episodio
                res = await db.execute(select(Episode).where(Episode.id == episode_id))
                ep = res.scalar_one_or_none()

                if ep:
                    # Actualizar la columna recomendacion_modelo sin errores
                    await db.execute(
                        update(Episode)
                        .where(Episode.id == ep.id)
                        .values(recomendacion_modelo=result.get("label"))
                    )
                    await db.commit()
                    result["update_episode"] = (
                        f"Model recommendation added to the episode of id {episode_id}"
                    )
                else:
                    # Si no existe, no falla
                    result["update_episode"] = (
                        f"Episode with id_episodio '{episode_id}' not found"
                    )

            except SQLAlchemyError as e:
                await db.rollback()
                result["update_episode"] = (
                    f"Could not update episode due to DB error: {str(e)}"
                )
            except Exception as e:
                result["update_episode"] = (
                    f"Unexpected error updating episode: {str(e)}"
                )

            finally:
                print(result)
                return result

        else:
            result["update_episode"] = f"Episode with id {episode_id} was not found"
            print(result)
            return result

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al realizar la predicción: {str(e)}",
        )
