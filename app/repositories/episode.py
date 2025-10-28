from datetime import date
from typing import Dict, List, Optional, Tuple

from sqlalchemy import func, insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.databases.postgresql.models import (
    Diagnostic,
    Episode,
    User,
    UserEpisodeValidation,
    episode_user,
)


class EpisodeRepository:
    # Create
    @staticmethod
    async def create(
        db: AsyncSession,
        *,
        data: dict,  # campos de Episode
        diagnostics_ids: Optional[List[int]] = None,
    ) -> Episode:
        stmt_all_nums = select(Episode.numero_episodio)
        result = await db.execute(stmt_all_nums)
        all_nums_str = result.scalars().all()
        max_num = 0
        if all_nums_str:
            try:
                numeric_nums = [
                    int(n) for n in all_nums_str if isinstance(n, str) and n.isdigit()
                ]
                if numeric_nums:
                    max_num = max(numeric_nums)
            except ValueError:
                pass

        new_episode_number = max_num + 1
        data["numero_episodio"] = str(new_episode_number)

        if "patient_id" not in data or data["patient_id"] is None:
            raise ValueError(
                "El campo 'patient_id' es obligatorio para crear un episodio y no fue entregado."
            )

        current_date = date.today()
        if "fecha_ingreso" not in data or data["fecha_ingreso"] is None:
            data["fecha_ingreso"] = current_date

        if "mes_ingreso" not in data or data["mes_ingreso"] is None:
            data["mes_ingreso"] = current_date.month

        if "estado_del_caso" not in data or data["estado_del_caso"] is None:
            data["estado_del_caso"] = "Abierto"

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

    @staticmethod
    async def get_by_patient_id(db: AsyncSession, patient_id: int) -> list[Episode]:
        res = await db.execute(select(Episode).where(Episode.patient_id == patient_id))
        return res.scalars().all()

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
        Todos los episodios de un paciente, con diagnostics, equipo y validador cargados.
        """
        stmt = (
            select(Episode)
            .where(Episode.patient_id == patient_id)
            .options(
                selectinload(Episode.diagnostics),
                selectinload(Episode.team_users),  # doctores asignados (episode_user)
                joinedload(Episode.validated_by).joinedload(
                    UserEpisodeValidation.user
                ),  # validador (user)
            )
            .order_by(Episode.id.desc())
        )
        res = await db.execute(stmt)
        return res.scalars().all()

    @staticmethod
    async def create_with_team(
        db: AsyncSession,
        *,
        data: dict,
        diagnostics_ids: Optional[List[int]] = None,
        doctors_by_turn: Optional[Dict[str, int]] = None,
    ) -> Episode:
        """
        Crea un episodio y asigna doctores (user_ids) recibidos por turno en episode_user.
        No valida que el user.turn coincida con la clave del dict; sólo que el user exista.
        """
        async with db.begin():
            ep = Episode(**data)

            # Asocia diagnósticos si vienen
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
            await db.flush()  # para tener ep.id

            # Asigna doctores si vienen
            if doctors_by_turn:
                # quedarnos con valores (user_ids) válidos y únicos
                user_ids = sorted({uid for uid in doctors_by_turn.values() if uid})
                if user_ids:
                    existing_ids = (
                        (await db.execute(select(User.id).where(User.id.in_(user_ids))))
                        .scalars()
                        .all()
                    )
                    if existing_ids:
                        values = [
                            {"episode_id": ep.id, "user_id": uid}
                            for uid in existing_ids
                        ]
                        await db.execute(insert(episode_user), values)

        # refrescamos relaciones útiles para la respuesta
        await db.refresh(ep, attribute_names=["diagnostics", "team_users"])
        return ep
