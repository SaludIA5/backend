from datetime import date
from typing import Optional

from pydantic import BaseModel


class ModelVersionBase(BaseModel):
    version: str
    stage: str
    metric: str
    metric_value: float
    trained_at: date
    active: bool = False


class ModelVersionCreate(ModelVersionBase):
    pass


class ModelVersionUpdate(BaseModel):
    metric: Optional[str] = None
    metric_value: Optional[float] = None
    trained_at: Optional[date] = None
    active: Optional[bool] = None
    stage: Optional[str] = None


class ModelVersionOut(ModelVersionBase):
    id: int
    version: Optional[str] = None
    metric: Optional[str] = None
    metric_value: Optional[float] = None
    trained_at: Optional[date] = None
    active: Optional[bool] = None
    stage: Optional[str] = None

    class Config:
        from_attributes = True


class ModelVersionSummary(BaseModel):
    version: str
    trained_at: date
    metric: str
    metric_value: float
    active: bool
