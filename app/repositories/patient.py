from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.databases.postgresql.models import Patient


class PatientRepository:
    # Create
    @staticmethod
    async def create(db: AsyncSession, *, name: str, rut: str, age: Optional[int] = None) -> Patient:
        instance = Patient(name=name, rut=rut, age=age, active=True)
        db.add(instance)
        try:
            await db.commit()
        except IntegrityError as e:
            await db.rollback()
            raise e
        await db.refresh(instance)
        return instance

    # Read
    @staticmethod
    async def get_by_id(db: AsyncSession, patient_id: int) -> Optional[Patient]:
        res = await db.execute(select(Patient).where(Patient.id == patient_id))
        return res.scalar_one_or_none()

    @staticmethod
    async def get_by_rut(db: AsyncSession, rut: str) -> Optional[Patient]:
        res = await db.execute(select(Patient).where(Patient.rut == rut))
        return res.scalar_one_or_none()

    # List paginated (+ search, + optional active filter)
    @staticmethod
    async def list_paginated(
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        active: Optional[bool] = None,
        order_desc: bool = True,
    ) -> Tuple[List[Patient], int]:
        query = select(Patient)
        count_q = select(func.count(Patient.id))

        if search:
            like = f"%{search}%"
            cond = (Patient.name.ilike(like)) | (Patient.rut.ilike(like))
            query = query.where(cond)
            count_q = count_q.where(cond)

        if active is not None:
            query = query.where(Patient.active == active)
            count_q = count_q.where(Patient.active == active)

        query = query.order_by(Patient.id.desc() if order_desc else Patient.id.asc())

        total_items = (await db.execute(count_q)).scalar_one()
        result = await db.execute(query.offset((page - 1) * page_size).limit(page_size))
        items = result.scalars().all()
        return items, total_items

    # Update
    @staticmethod
    async def update_partial(
        db: AsyncSession,
        patient: Patient,
        *,
        name: Optional[str] = None,
        rut: Optional[str] = None,
        age: Optional[int] = None,
        active: Optional[bool] = None,
    ) -> Patient:
        if name is not None:
            patient.name = name
        if rut is not None:
            patient.rut = rut
        if age is not None:
            patient.age = age
        if active is not None:
            patient.active = active
        try:
            await db.commit()
        except IntegrityError as e:
            await db.rollback()
            raise e
        await db.refresh(patient)
        return patient

    # Delete
    @staticmethod
    async def hard_delete(db: AsyncSession, patient: Patient) -> None:
        db.delete(patient)
        await db.commit()
