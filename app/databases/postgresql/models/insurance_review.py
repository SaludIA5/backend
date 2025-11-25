from sqlalchemy import Boolean, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .base import BaseModel


class InsuranceReview(BaseModel):
    __tablename__ = "insurance_reviews"

    episode_id = Column(
        Integer,
        ForeignKey("episodes.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    is_pertinent = Column(Boolean, nullable=False)

    episode = relationship("Episode", back_populates="insurance_review")
