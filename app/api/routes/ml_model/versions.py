from fastapi import APIRouter

router = APIRouter(prefix="/versions", tags=["ML Model - Versions"])

@router.get("/")
async def list_versions():
    return {"versions": []}