from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.databases.postgresql.db import get_db
from app.databases.postgresql.models import Episode

router = APIRouter(prefix="/episodes", tags=["episodes"])

@router.post("/")
async def create_episode(patient_id: int, numero_episodio: str, db: AsyncSession = Depends(get_db)):
    new_episode = Episode(patient_id=patient_id, numero_episodio=numero_episodio)
    db.add(new_episode)
    await db.commit()
    await db.refresh(new_episode)
    return new_episode

@router.get("/")
async def list_episodes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Episode))
    return result.scalars().all()

@router.get("/{episode_id}")
async def get_episode(episode_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Episode).where(Episode.id == episode_id))
    episode = result.scalar_one_or_none()
    if not episode:
        raise HTTPException(404, "Episode not found")
    return episode
