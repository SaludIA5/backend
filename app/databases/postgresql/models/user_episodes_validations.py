from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .base import BaseModel


class UserEpisodeValidation(BaseModel):
    __tablename__ = "user_episodes_validations"

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    episode_id = Column(
        Integer,
        ForeignKey("episodes.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    user = relationship("User", back_populates="episodes_validations")
    episode = relationship("Episode", back_populates="validated_by")
