from fastapi import APIRouter

router = APIRouter(prefix="/training", tags=["ML Model - Training"])

@router.post("/run")
async def run_training():
    return {"status": "training started"}