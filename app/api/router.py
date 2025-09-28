from fastapi import APIRouter  
from .routes.patients import router as patients_router
from .routes.diagnostics import router as diagnostics_router
from .routes.episodes import router as episodes_router
from .routes.users import router as users_router

router = APIRouter() 
router.include_router(patients_router)
router.include_router(diagnostics_router)
router.include_router(episodes_router)
router.include_router(users_router)