from fastapi import APIRouter

router = APIRouter(prefix="/inference",tags=["ML Model - Inference"])

@router.get("/predict")
async def predict():
    return {"status": "inference OK"}