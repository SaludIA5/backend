from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship

from .base import BaseModel


class DoctorSummary(BaseModel):
    __tablename__ = "doctor_summaries"

    episode_id = Column(
        Integer,
        ForeignKey("episodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    comment = Column(Text, nullable=False)

    # Relaciones (ajusta los nombres de los modelos si en tu proyecto son distintos)
    episode = relationship("Episode", back_populates="doctor_summaries")
    user = relationship("User", back_populates="doctor_summaries")
