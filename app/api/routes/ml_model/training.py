from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from app.databases.postgresql.models import User
from app.services.auth_service import require_admin_role
from app.services.ml_model_services.training_service import TrainingService

router = APIRouter(prefix="/training", tags=["ML Model - Training"])

@router.post("/", status_code=status.HTTP_200_OK)
async def trigger_training(
    current_user: Annotated[User, Depends(require_admin_role)],
    stage: str = "dev",
):
    """
    Launch the ML model training pipeline manually via endpoint.
    """
    if current_user is None or not getattr(current_user, "is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required to train models",
        )
    try:
        service = TrainingService(stage=stage)
        result = await service.run_training()

        return {
            "status": "success",
            "stage": stage,
            "trained_version": result.version,
            "trained_at": str(result.trained_at),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error running training pipeline: {str(e)}",
        )