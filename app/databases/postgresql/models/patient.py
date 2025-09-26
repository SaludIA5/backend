from sqlalchemy import String, Integer, Boolean, Column
from sqlalchemy.orm import relationship
from .base import BaseModel

class Patient(BaseModel):
    __tablename__ = "patients"

    name = Column(String(120), nullable=False, index=True)
    rut = Column(String(20), nullable=False, unique=True, index=True)
    age = Column(Integer, nullable=False)
    active = Column(Boolean, nullable=False, server_default="true")

    episodes = relationship("Episode", back_populates="patient", cascade="all, delete-orphan")