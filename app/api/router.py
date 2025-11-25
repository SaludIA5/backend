from fastapi import APIRouter

from .routes.auth import router as auth_router
from .routes.diagnostics import router as diagnostics_router
from .routes.episodes import router as episodes_router
from .routes.metrics import router as metrics_router
from .routes.ml_model import router as ml_model_router
from .routes.patients import router as patients_router
from .routes.predictions import router as predictions_router
from .routes.users import router as users_router
from .routes.doctor_summary import router as doctor_summary_router

router = APIRouter()
router.include_router(patients_router)
router.include_router(diagnostics_router)
router.include_router(episodes_router)
router.include_router(users_router)
router.include_router(auth_router)
router.include_router(predictions_router)
router.include_router(metrics_router)
router.include_router(ml_model_router)
router.include_router(doctor_summary_router)
