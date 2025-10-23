from typing import List, Optional, Tuple

from passlib.hash import bcrypt
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.databases.postgresql.models import User


class UserRepository:
    # Create
    @staticmethod
    async def create(
        db: AsyncSession,
        *,
        name: str,
        email: str,
        rut: str,
        password: str,
        is_chief_doctor: bool = False,
        is_doctor: bool = False,
        turn: Optional[str] = None,
    ) -> User:
        instance = User(
            name=name,
            email=email,
            rut=rut,
            hashed_password=bcrypt.hash(password),
            is_chief_doctor=is_chief_doctor,
            is_doctor=is_doctor,
            turn=turn,
        )
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
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        res = await db.execute(select(User).where(User.id == user_id))
        return res.scalar_one_or_none()

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        res = await db.execute(select(User).where(User.email == email))
        return res.scalar_one_or_none()

    # List paginated + search (name/email)
    @staticmethod
    async def list_paginated(
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        order_desc: bool = True,
    ) -> Tuple[List[User], int]:
        query = select(User)
        count_q = select(func.count(User.id))

        if search:
            like = f"%{search}%"
            from sqlalchemy import or_

            cond = or_(
                User.name.ilike(like),
                User.email.ilike(like),
                User.rut.ilike(like),
                User.turn.ilike(like),
            )
            query = query.where(cond)
            count_q = count_q.where(cond)

        query = query.order_by(User.id.desc() if order_desc else User.id.asc())

        total_items = (await db.execute(count_q)).scalar_one()
        result = await db.execute(query.offset((page - 1) * page_size).limit(page_size))
        items = result.scalars().all()
        return items, total_items

    # Update
    @staticmethod
    async def update_partial(
        db: AsyncSession,
        user: User,
        *,
        name: Optional[str] = None,
        email: Optional[str] = None,
        rut: Optional[str] = None,
        password: Optional[str] = None,
        is_chief_doctor: Optional[bool] = None,
        is_doctor: Optional[bool] = None,
        turn: Optional[str] = None,
    ) -> User:
        if name is not None:
            user.name = name
        if email is not None:
            user.email = email
        if rut is not None:
            user.rut = rut
        if is_chief_doctor is not None:
            user.is_chief_doctor = is_chief_doctor
        if is_doctor is not None:
            user.is_doctor = is_doctor
        if turn is not None:
            user.turn = turn
        if password is not None:
            user.hashed_password = bcrypt.hash(password)

        try:
            await db.commit()
        except IntegrityError as e:
            await db.rollback()
            raise e
        await db.refresh(user)
        return user

    # Delete
    @staticmethod
    async def hard_delete(db: AsyncSession, user: User) -> None:
        db.delete(user)
        await db.commit()

