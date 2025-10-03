import re
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

EMAIL_REGEX = re.compile(r"^[^@]+@[^@]+\.[^@]+$")


# -------- Inputs --------
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    email: str
    is_chief_doctor: bool = False
    is_doctor: bool = False

    @field_validator("email")
    def validate_email(cls, v: str):
        if not EMAIL_REGEX.match(v):
            raise ValueError("Invalid email format")
        return v


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    email: Optional[str] = None
    is_chief_doctor: Optional[bool] = None
    is_doctor: Optional[bool] = None

    @field_validator("email")
    def validate_email(cls, v: Optional[str]):
        if v is not None and not EMAIL_REGEX.match(v):
            raise ValueError("Invalid email format")
        return v


# -------- Outputs --------
class UserOut(BaseModel):
    id: int
    name: str
    email: str
    is_chief_doctor: bool
    is_doctor: bool

    class Config:
        from_attributes = True


class UserPageMeta(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int


class UserPage(BaseModel):
    items: List[UserOut]
    meta: UserPageMeta
