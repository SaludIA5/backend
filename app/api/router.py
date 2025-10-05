from fastapi import APIRouter

from .routes.diagnostics import router as diagnostics_router
from .routes.episodes import router as episodes_router
from .routes.patients import router as patients_router
from .routes.predictions import router as predictions_router
from .routes.users import router as users_router
from .routes.auth import router as auth_router

router = APIRouter()
router.include_router(patients_router)
router.include_router(diagnostics_router)
router.include_router(episodes_router)
router.include_router(users_router)
router.include_router(auth_router)
router.include_router(predictions_router)
