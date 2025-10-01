from typing import Optional, List
from pydantic import BaseModel, Field

# -------- Inputs --------
class DiagnosticCreate(BaseModel):
    cie_code: str = Field(..., min_length=1, max_length=20)
    description: Optional[str] = Field(None, max_length=500)

class DiagnosticUpdate(BaseModel):
    cie_code: Optional[str] = Field(None, min_length=1, max_length=20)
    description: Optional[str] = Field(None, max_length=500)

# -------- Outputs --------
class DiagnosticOut(BaseModel):
    id: int
    cie_code: str
    description: Optional[str] = None

    class Config:
        from_attributes = True  # para mapear desde SQLAlchemy

class DiagnosticPageMeta(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int

class DiagnosticPage(BaseModel):
    items: List[DiagnosticOut]
    meta: DiagnosticPageMeta
