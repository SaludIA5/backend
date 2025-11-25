from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class InsuranceReviewBase(BaseModel):
    is_pertinent: bool


class InsuranceReviewCreate(InsuranceReviewBase):
    episode_id: int


class InsuranceReviewResponse(InsuranceReviewBase):
    id: int
    episode_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class InsuranceReviewUpdate(BaseModel):
    is_pertinent: bool
