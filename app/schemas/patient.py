from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from .user import UserOut


# -------- Inputs --------
class PatientCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    rut: str = Field(
        ..., min_length=3, max_length=20, description="RUT sin puntos, con guión"
    )
    age: Optional[int] = Field(None, ge=0, le=130)


class PatientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
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


# -------- Combined Request --------
class PatientWithEpisodeCreate(BaseModel):
    """Schema for creating a patient with an empty episode and doctor assignments."""

    # Patient fields
    name: str = Field(..., min_length=1, max_length=120)
    rut: str = Field(
        ..., min_length=3, max_length=20, description="RUT sin puntos, con guión"
    )
    age: Optional[int] = Field(None, ge=0, le=130)
    gender: Optional[str] = Field(None, max_length=20)

    # Doctor assignments by turn
    doctors: Dict[str, int] = Field(
        ...,
        description="Mapa de turnos a IDs de doctores. Ej: {'turnoa': 1, 'turnob': 2, 'turnoc': 3}",
        min_length=1,
        max_length=3,
    )


# -------- Combined Response --------
class PatientWithEpisodeResponse(BaseModel):
    """Response schema for patient with episode creation."""

    patient: PatientOut
    episode_id: int
    episode_number: str
    assigned_doctors: List[UserOut]

    class Config:
        from_attributes = True
