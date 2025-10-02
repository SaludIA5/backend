from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.databases.postgresql.db import get_db
from app.repositories.episode import EpisodeRepository
from app.schemas.episode import (
    EpisodeCreate,
    EpisodeOut,
    EpisodePage,
    EpisodePageMeta,
    EpisodeUpdate,
)

router = APIRouter(prefix="/episodes", tags=["episodes"])


def _total_pages(total: int, size: int) -> int:
    return (total + size - 1) // size if size else 1


# CREATE
@router.post("/", response_model=EpisodeOut, status_code=status.HTTP_201_CREATED)
async def create_episode(
    payload: EpisodeCreate, db: Annotated[AsyncSession, Depends(get_db)]
):
    try:
        ep = await EpisodeRepository.create(
            db,
            data=payload.model_dump(exclude={"diagnostics_ids"}, exclude_unset=True),
            diagnostics_ids=payload.diagnostics_ids,
        )
        return ep
    except IntegrityError:
        raise HTTPException(status_code=409, detail="numero_episodio ya registrado")


# LIST (paginada + filtros)
@router.get("/", response_model=EpisodePage)
async def list_episodes(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = None,
    patient_id: int | None = None,
):
    items, total = await EpisodeRepository.list_paginated(
        db, page=page, page_size=page_size, search=search, patient_id=patient_id
    )
    return EpisodePage(
        items=items,
        meta=EpisodePageMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=_total_pages(total, page_size),
        ),
    )


# GET by ID
@router.get("/{episode_id}", response_model=EpisodeOut)
async def get_episode(episode_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    ep = await EpisodeRepository.get_by_id(db, episode_id)
    if not ep:
        raise HTTPException(status_code=404, detail="Episode not found")
    return ep


# UPDATE
@router.patch("/{episode_id}", response_model=EpisodeOut)
async def update_episode(
    episode_id: int,
    payload: EpisodeUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    ep = await EpisodeRepository.get_by_id(db, episode_id)
    if not ep:
        raise HTTPException(status_code=404, detail="Episode not found")
    try:
        return await EpisodeRepository.update_partial(
            db,
            ep,
            data=payload.model_dump(exclude={"diagnostics_ids"}, exclude_unset=True),
            diagnostics_ids=payload.diagnostics_ids,
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail="numero_episodio ya registrado")


# DELETE
@router.delete("/{episode_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_episode(episode_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    ep = await EpisodeRepository.get_by_id(db, episode_id)
    if not ep:
        raise HTTPException(status_code=404, detail="Episode not found")
    await EpisodeRepository.hard_delete(db, ep)
    return None
