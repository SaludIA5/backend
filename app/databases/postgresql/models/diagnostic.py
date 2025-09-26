from sqlalchemy import String, Integer, Column
from .base import BaseModel

class Diagnostic(BaseModel):
    __tablename__ = "diagnostics"

    cie_code = Column(String(20), nullable=False, unique=True, index=True)
    description = Column(String(500), nullable=True)