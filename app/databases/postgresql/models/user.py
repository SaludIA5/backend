from sqlalchemy import Boolean, Column, String

from .base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    name = Column(String(120), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    rut = Column(String(20), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_chief_doctor = Column(Boolean, default=False)
    is_doctor = Column(Boolean, default=False)
