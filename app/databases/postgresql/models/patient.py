from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from .base import BaseModel


class Patient(BaseModel):
    __tablename__ = "patients"

    name = Column(String(120), nullable=False, index=True)
    rut = Column(String(20), nullable=True, unique=True, index=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    active = Column(Boolean, nullable=False, server_default="true")

    episodes = relationship(
        "Episode", back_populates="patient", cascade="all, delete-orphan"
    )
