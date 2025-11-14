from sqlalchemy import Boolean, Column, Date, Float, String

from app.databases.postgresql.base import BaseModel


class ModelVersion(BaseModel):
    __tablename__ = "model_versions"

    version = Column(String(50), nullable=False, unique=True, index=True)
    metric = Column(String(50), nullable=False)
    metric_value = Column(Float, nullable=False)
    trained_at = Column(Date, nullable=False)
    active = Column(Boolean, default=False)
