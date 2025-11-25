from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship

from .base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    name = Column(String(120), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    rut = Column(String(20), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_chief_doctor = Column(Boolean, default=False)
    is_doctor = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    turn = Column(String(50), nullable=True)

    episodes_validations = relationship(
        "UserEpisodeValidation", back_populates="user", cascade="all, delete-orphan"
    )

    assigned_episodes = relationship(
        "Episode", secondary="episode_user", back_populates="team_users"
    )

    doctor_summaries = relationship(
        "DoctorSummary", back_populates="user", cascade="all, delete-orphan"
    )
