from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.databases.postgresql.db import get_db
from app.databases.postgresql.models import User
from app.repositories.model_versions import ModelVersionRepository
from app.schemas.ml_model.versions import (
    ModelVersionCreate,
    ModelVersionOut,
    ModelVersionSummary,
    ModelVersionUpdate,
)
from app.services.auth_service import require_admin

router = APIRouter(prefix="/versions", tags=["ML Model - Versions"])


@router.post("/", response_model=ModelVersionOut, status_code=201)
async def create_model_version(
    payload: ModelVersionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
):
    try:
        return await ModelVersionRepository.create(
            db,
            version=payload.version,
            stage=payload.stage,
            metric=payload.metric,
            metric_value=payload.metric_value,
            trained_at=payload.trained_at,
            active=payload.active,
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Version already exists")


@router.get("/", response_model=List[ModelVersionOut])
async def list_all_versions(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
):
    return await ModelVersionRepository.list_all(db)


@router.get("/stage/{stage}", response_model=List[ModelVersionOut])
async def list_versions_by_stage(
    stage: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
):
    if stage not in ["dev", "prod"]:
        raise HTTPException(status_code=400, detail="Invalid stage")

    return await ModelVersionRepository.list_by_stage(db, stage)


@router.get("/{version}", response_model=ModelVersionOut)
async def get_version(
    version: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
):
    obj = await ModelVersionRepository.get_by_version(db, version)
    if not obj:
        raise HTTPException(status_code=404, detail="Version not found")
    return obj


@router.patch("/{version}", response_model=ModelVersionOut)
async def update_version(
    version: str,
    payload: ModelVersionUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
):
    instance = await ModelVersionRepository.get_by_version(db, version)
    if not instance:
        raise HTTPException(status_code=404, detail="Version not found")

    try:
        return await ModelVersionRepository.update_partial(
            db,
            instance,
            **payload.model_dump(exclude_unset=True),
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Integrity error")


@router.post("/{version}/activate", response_model=ModelVersionOut)
async def activate_version(
    version: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
):
    instance = await ModelVersionRepository.get_by_version(db, version)
    if not instance:
        raise HTTPException(status_code=404, detail="Version not found")

    # desactivar todas las del mismo stage
    versions = await ModelVersionRepository.list_by_stage(db, instance.stage)
    for mv in versions:
        mv.active = mv.version == version

    await db.commit()
    await db.refresh(instance)
    return instance


@router.delete("/{version}", status_code=204)
async def delete_version(
    version: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
):
    obj = await ModelVersionRepository.get_by_version(db, version)
    if not obj:
        raise HTTPException(status_code=404, detail="Version not found")

    await ModelVersionRepository.delete_by_version(db, version)
    return None


@router.delete("/stage/{stage}", status_code=204)
async def delete_stage(
    stage: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
):
    if stage not in ["dev", "prod"]:
        raise HTTPException(status_code=400, detail="Invalid stage")

    await ModelVersionRepository.delete_by_stage(db, stage)
    return None


@router.get("/prod/summary", response_model=List[ModelVersionSummary])
async def list_prod_versions_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
):
    """
    Retorna todas las versiones en producción con:
    - version
    - trained_at
    - metric
    - metric_value
    - active
    """
    versions = await ModelVersionRepository.list_prod(db)

    return [
        ModelVersionSummary(
            version=v.version,
            trained_at=v.trained_at,
            metric=v.metric,
            metric_value=v.metric_value,
            active=v.active,
        )
        for v in versions
    ]
