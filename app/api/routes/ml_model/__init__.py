from fastapi import APIRouter

from app.api.routes.ml_model.inference import router as inference_router
from app.api.routes.ml_model.training import router as training_router
from app.api.routes.ml_model.versions import router as versions_router

router = APIRouter(prefix="/ml-model")

router.include_router(inference_router)
router.include_router(training_router)
router.include_router(versions_router)