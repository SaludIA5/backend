from datetime import datetime

from pydantic import BaseModel, Field


class DoctorSummaryBase(BaseModel):
    episode_id: int = Field(..., ge=1)
    user_id: int = Field(..., ge=1)
    comment: str = Field(..., min_length=1)


class DoctorSummaryCreate(DoctorSummaryBase):
    pass


class DoctorSummaryRead(DoctorSummaryBase):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
