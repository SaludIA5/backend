from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.databases.postgresql.models import Diagnostic, Episode


class EpisodeRepository:
    # Create
    @staticmethod
    async def create(
        db: AsyncSession,
        *,
        data: dict,  # campos de Episode
        diagnostics_ids: Optional[List[int]] = None,
    ) -> Episode:
        ep = Episode(**data)
        if diagnostics_ids:
            diags = (
                (
                    await db.execute(
                        select(Diagnostic).where(Diagnostic.id.in_(diagnostics_ids))
                    )
                )
                .scalars()
                .all()
            )
            ep.diagnostics = diags

        db.add(ep)
        try:
            await db.commit()
        except IntegrityError as e:
            await db.rollback()
            # ej: numero_episodio único
            raise e
        await db.refresh(ep)
        return ep

    # Read
    @staticmethod
    async def get_by_id(db: AsyncSession, episode_id: int) -> Optional[Episode]:
        res = await db.execute(
            select(Episode)
            .options(selectinload(Episode.diagnostics))
            .where(Episode.id == episode_id)
        )
        return res.scalar_one_or_none()

    @staticmethod
    async def get_by_numero(
        db: AsyncSession, numero_episodio: str
    ) -> Optional[Episode]:
        res = await db.execute(
            select(Episode)
            .options(selectinload(Episode.diagnostics))
            .where(Episode.numero_episodio == numero_episodio)
        )
        return res.scalar_one_or_none()

    # List paginated + filtros
    @staticmethod
    async def list_paginated(
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 10,
        search: Optional[
            str
        ] = None,  # busca por numero_episodio / estado_del_caso / centro
        patient_id: Optional[int] = None,
        order_desc: bool = True,
    ) -> Tuple[List[Episode], int]:
        query = select(Episode).options(selectinload(Episode.diagnostics))
        count_q = select(func.count(Episode.id))

        if search:
            like = f"%{search}%"
            from sqlalchemy import or_

            cond = or_(
                Episode.numero_episodio.ilike(like),
                Episode.estado_del_caso.ilike(like),
                Episode.centro.ilike(like),
            )
            query = query.where(cond)
            count_q = count_q.where(cond)

        if patient_id is not None:
            query = query.where(Episode.patient_id == patient_id)
            count_q = count_q.where(Episode.patient_id == patient_id)

        query = query.order_by(Episode.id.desc() if order_desc else Episode.id.asc())

        total_items = (await db.execute(count_q)).scalar_one()
        result = await db.execute(query.offset((page - 1) * page_size).limit(page_size))
        items = result.scalars().all()
        return items, total_items

    # Update
    @staticmethod
    async def update_partial(
        db: AsyncSession,
        ep: Episode,
        *,
        data: dict,  # campos simples a actualizar
        diagnostics_ids: Optional[List[int]] = None,  # si viene, reemplaza asociaciones
    ) -> Episode:
        # Asignar campos simples
        for k, v in data.items():
            setattr(ep, k, v)

        # Actualizar M2M
        if diagnostics_ids is not None:
            diags = (
                (
                    await db.execute(
                        select(Diagnostic).where(Diagnostic.id.in_(diagnostics_ids))
                    )
                )
                .scalars()
                .all()
            )
            ep.diagnostics = diags

        try:
            await db.commit()
        except IntegrityError as e:
            await db.rollback()
            raise e

        await db.refresh(ep)
        return ep

    # Delete
    @staticmethod
    async def hard_delete(db: AsyncSession, ep: Episode) -> None:
        db.delete(ep)
        await db.commit()
