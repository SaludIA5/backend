from typing import Optional, List
from pydantic import BaseModel, Field

# -------- Inputs --------
class PatientCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    rut: str = Field(..., min_length=3, max_length=20, description="RUT sin puntos, con guión")
    age: int = Field(..., ge=0, le=130)

class PatientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    rut: Optional[str] = Field(None, min_length=3, max_length=20)
    age: Optional[int] = Field(None, ge=0, le=130)
    active: Optional[bool] = None

# -------- Outputs --------
class PatientOut(BaseModel):
    id: int
    name: str
    rut: str
    age: int
    active: bool
    class Config:
        from_attributes = True  # (Pydantic v2)

class PatientPageMeta(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int

class PatientPage(BaseModel):
    items: List[PatientOut]
    meta: PatientPageMeta
