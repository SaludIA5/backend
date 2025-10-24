from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.databases.postgresql.db import get_db
from app.repositories.metric import MetricRepository
from app.schemas.metric import (
    EpisodeMetrics,
    MetricPage,
    MetricPageMeta,
    MetricsSummary,
    RecommendationMetrics,
    ValidationMetrics,
)

router = APIRouter(prefix="/metrics", tags=["metrics"])


def _total_pages(total: int, size: int) -> int:
    return (total + size - 1) // size if size else 1


# ENDPOINTS DE MÉTRICAS DE RECOMENDACIONES DE IA


@router.get("/recommendations", response_model=RecommendationMetrics)
async def get_recommendation_metrics(
    db: Annotated[AsyncSession, Depends(get_db)],
    start_date: datetime | None = Query(
        None, description="Fecha de inicio del período"
    ),
    end_date: datetime | None = Query(None, description="Fecha de fin del período"),
):
    """Obtiene métricas detalladas de recomendaciones de IA"""
    try:
        metrics = await MetricRepository.get_recommendation_metrics(
            db, start_date=start_date, end_date=end_date
        )
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener métricas de recomendaciones: {str(e)}",
        )


@router.get("/validation-by-doctor", response_model=list[ValidationMetrics])
async def get_validation_metrics_by_doctor(
    db: Annotated[AsyncSession, Depends(get_db)],
    start_date: datetime | None = Query(
        None, description="Fecha de inicio del período"
    ),
    end_date: datetime | None = Query(None, description="Fecha de fin del período"),
):
    """Obtiene métricas de validaciones agrupadas por médico"""
    try:
        metrics = await MetricRepository.get_validation_metrics_by_doctor(
            db, start_date=start_date, end_date=end_date
        )
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener métricas por médico: {str(e)}",
        )


@router.get("/episodes", response_model=list[EpisodeMetrics])
async def get_episode_metrics(
    db: Annotated[AsyncSession, Depends(get_db)],
    start_date: datetime | None = Query(
        None, description="Fecha de inicio del período"
    ),
    end_date: datetime | None = Query(None, description="Fecha de fin del período"),
    limit: int = Query(
        100, ge=1, le=1000, description="Límite de episodios a retornar"
    ),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
):
    """Obtiene métricas detalladas por episodio"""
    try:
        metrics = await MetricRepository.get_episode_metrics(
            db, start_date=start_date, end_date=end_date, limit=limit, offset=offset
        )
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener métricas por episodio: {str(e)}",
        )


@router.get("/summary", response_model=MetricsSummary)
async def get_metrics_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
    start_date: datetime | None = Query(
        None, description="Fecha de inicio del período"
    ),
    end_date: datetime | None = Query(None, description="Fecha de fin del período"),
):
    """Obtiene resumen completo de todas las métricas"""
    try:
        summary = await MetricRepository.get_metrics_summary(
            db, start_date=start_date, end_date=end_date
        )
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener resumen de métricas: {str(e)}",
        )


# ENDPOINTS BÁSICOS DE MÉTRICAS (para compatibilidad)


@router.get("/", response_model=MetricPage)
async def list_metrics(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = None,
):
    """Lista métricas básicas (implementación básica para compatibilidad)"""
    try:
        items, total = await MetricRepository.list_paginated(
            db, page=page, page_size=page_size, search=search
        )
        return MetricPage(
            items=items,
            meta=MetricPageMeta(
                page=page,
                page_size=page_size,
                total=total,
                total_pages=_total_pages(total, page_size),
            ),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar métricas: {str(e)}",
        )
