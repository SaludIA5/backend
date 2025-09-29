from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.databases.postgresql.db import get_db
from app.schemas.diagnostic import (
    DiagnosticCreate, DiagnosticUpdate, DiagnosticOut, DiagnosticPage, PageMeta
)
from app.repositories.diagnostic import DiagnosticRepository

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])

def _total_pages(total: int, size: int) -> int:
    return (total + size - 1) // size if size else 1

# CREATE
@router.post("/", response_model=DiagnosticOut, status_code=status.HTTP_201_CREATED)
async def create_diagnostic(payload: DiagnosticCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        return await DiagnosticRepository.create(
            db, cie_code=payload.cie_code, description=payload.description
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail="CIE code ya registrado")

# LIST (con paginación + búsqueda opcional)
@router.get("/", response_model=DiagnosticPage)
async def list_diagnostics(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = None,
):
    items, total = await DiagnosticRepository.list_paginated(
        db, page=page, page_size=page_size, search=search
    )
    return DiagnosticPage(
        items=items,
        meta=PageMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=_total_pages(total, page_size),
        ),
    )

# GET by ID
@router.get("/{diag_id}", response_model=DiagnosticOut)
async def get_diagnostic(diag_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    diag = await DiagnosticRepository.get_by_id(db, diag_id)
    if not diag:
        raise HTTPException(status_code=404, detail="Diagnostic not found")
    return diag

# UPDATE
@router.patch("/{diag_id}", response_model=DiagnosticOut)
async def update_diagnostic(diag_id: int, payload: DiagnosticUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    diag = await DiagnosticRepository.get_by_id(db, diag_id)
    if not diag:
        raise HTTPException(status_code=404, detail="Diagnostic not found")
    try:
        return await DiagnosticRepository.update_partial(
            db, diag, **payload.model_dump(exclude_unset=True)
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail="CIE code ya registrado")

# DELETE
@router.delete("/{diag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_diagnostic(diag_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    diag = await DiagnosticRepository.get_by_id(db, diag_id)
    if not diag:
        raise HTTPException(status_code=404, detail="Diagnostic not found")
    await DiagnosticRepository.hard_delete(db, diag)
    return None

