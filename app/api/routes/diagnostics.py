from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.databases.postgresql.db import get_db
from app.databases.postgresql.models import Diagnostic

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])

@router.post("/")
async def create_diagnostic(cie_code: str, description: str | None = None, db: AsyncSession = Depends(get_db)):
    new_diag = Diagnostic(cie_code=cie_code, description=description)
    db.add(new_diag)
    await db.commit()
    await db.refresh(new_diag)
    return new_diag

@router.get("/")
async def list_diagnostics(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Diagnostic))
    return result.scalars().all()

@router.get("/{diag_id}")
async def get_diagnostic(diag_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Diagnostic).where(Diagnostic.id == diag_id))
    diag = result.scalar_one_or_none()
    if not diag:
        raise HTTPException(404, "Diagnostic not found")
    return diag
