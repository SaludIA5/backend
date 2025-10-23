from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.databases.postgresql.models import Diagnostic, Episode
from app.databases.postgresql.models import User, UserEpisodeValidation, episode_user


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
    
    @staticmethod
    async def list_by_doctor_validations(db, doctor_id: int):
        stmt = (
            select(Episode)
            .join(UserEpisodeValidation, UserEpisodeValidation.episode_id == Episode.id)
            .where(UserEpisodeValidation.user_id == doctor_id)
            .options(
                selectinload(Episode.diagnostics),
                joinedload(Episode.validated_by).joinedload(UserEpisodeValidation.user),
            )
            .order_by(Episode.id.desc())
        )
        res = await db.execute(stmt)
        return res.scalars().all()

    @staticmethod
    async def list_by_turn_validations(db, turn: str):
        stmt = (
            select(Episode)
            .join(UserEpisodeValidation, UserEpisodeValidation.episode_id == Episode.id)
            .join(User, User.id == UserEpisodeValidation.user_id)
            .where(User.is_doctor.is_(True), User.turn == turn)
            .options(
                selectinload(Episode.diagnostics),
                joinedload(Episode.validated_by).joinedload(UserEpisodeValidation.user),
            )
            .order_by(Episode.id.desc())
        )
        res = await db.execute(stmt)
        return res.scalars().all()

    @staticmethod
    async def list_all_with_validators(db):
        stmt = (
            select(Episode)
            .options(
                selectinload(Episode.diagnostics),
                joinedload(Episode.validated_by).joinedload(UserEpisodeValidation.user),
            )
            .order_by(Episode.id.desc())
        )
        res = await db.execute(stmt)
        return res.scalars().all()
    
    @staticmethod
    async def list_by_user_team(db, user_id: int):
        """
        Episodios donde 'user_id' está asignado vía episode_user.
        """
        stmt = (
            select(Episode)
            .join(episode_user, episode_user.c.episode_id == Episode.id)
            .where(episode_user.c.user_id == user_id)
            .options(
                selectinload(Episode.diagnostics),
                selectinload(Episode.team_users),  # carga todo el equipo
            )
            .order_by(Episode.id.desc())
        )
        res = await db.execute(stmt)
        return res.scalars().all()

    @staticmethod
    async def list_by_turn_team(db, turn: str):
        """
        Episodios donde hay al menos un User asignado (episode_user) con is_doctor=True y turn=turn.
        """
        stmt = (
            select(Episode)
            .join(episode_user, episode_user.c.episode_id == Episode.id)
            .join(User, User.id == episode_user.c.user_id)
            .where(User.is_doctor.is_(True), User.turn == turn)
            .options(
                selectinload(Episode.diagnostics),
                selectinload(Episode.team_users),  # carga todo el equipo
            )
            .order_by(Episode.id.desc())
        )
        res = await db.execute(stmt)
        return res.scalars().all()

    @staticmethod
    async def list_all_with_team(db):
        """
        Todos los episodios con su equipo (team_users) cargado.
        """
        stmt = (
            select(Episode)
            .options(
                selectinload(Episode.diagnostics),
                selectinload(Episode.team_users),
            )
            .order_by(Episode.id.desc())
        )
        res = await db.execute(stmt)
        return res.scalars().all()
    
    @staticmethod
    async def list_by_patient_id(db, patient_id: int):
        """
        Todos los episodios de un paciente, con diagnostics cargados.
        """
        stmt = (
            select(Episode)
            .where(Episode.patient_id == patient_id)
            .options(selectinload(Episode.diagnostics))
            .order_by(Episode.id.desc())
        )
        res = await db.execute(stmt)
        return res.scalars().all()