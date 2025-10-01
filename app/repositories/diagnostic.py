from typing import Optional, Tuple, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.databases.postgresql.models import Diagnostic

class DiagnosticRepository:
    # Create
    @staticmethod
    async def create(db: AsyncSession, *, cie_code: str, description: Optional[str]) -> Diagnostic:
        instance = Diagnostic(cie_code=cie_code, description=description)
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
    async def get_by_id(db: AsyncSession, diag_id: int) -> Optional[Diagnostic]:
        res = await db.execute(select(Diagnostic).where(Diagnostic.id == diag_id))
        return res.scalar_one_or_none()

    @staticmethod
    async def get_by_cie_code(db: AsyncSession, cie_code: str) -> Optional[Diagnostic]:
        res = await db.execute(select(Diagnostic).where(Diagnostic.cie_code == cie_code))
        return res.scalar_one_or_none()

    # List paginated + search
    @staticmethod
    async def list_paginated(
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        order_desc: bool = True,
    ) -> Tuple[List[Diagnostic], int]:
        query = select(Diagnostic)
        count_q = select(func.count(Diagnostic.id))

        if search:
            like = f"%{search}%"
            cond = (Diagnostic.cie_code.ilike(like)) | (Diagnostic.description.ilike(like))
            query = query.where(cond)
            count_q = count_q.where(cond)

        query = query.order_by(Diagnostic.id.desc() if order_desc else Diagnostic.id.asc())

        total_items = (await db.execute(count_q)).scalar_one()
        result = await db.execute(query.offset((page - 1) * page_size).limit(page_size))
        items = result.scalars().all()
        return items, total_items

    # Update (PATCH)
    @staticmethod
    async def update_partial(
        db: AsyncSession,
        diag: Diagnostic,
        *,
        cie_code: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Diagnostic:
        if cie_code is not None:
            diag.cie_code = cie_code
        if description is not None:
            diag.description = description
        try:
            await db.commit()
        except IntegrityError as e:
            await db.rollback()
            raise e
        await db.refresh(diag)
        return diag

    # Delete (hard)
    @staticmethod
    async def hard_delete(db: AsyncSession, diag: Diagnostic) -> None:
        await db.delete(diag)
        await db.commit()
