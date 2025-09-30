from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
import re

EMAIL_REGEX = re.compile(r"^[^@]+@[^@]+\.[^@]+$")

# -------- Inputs --------
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    email: str
    password: str = Field(..., min_length=6, max_length=255)
    role: str = Field(default="Otro", min_length=1, max_length=50)

    @field_validator("email")
    def validate_email(cls, v: str):
        if not EMAIL_REGEX.match(v):
            raise ValueError("Invalid email format")
        return v

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    email: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6, max_length=255)
    role: Optional[str] = Field(None, min_length=1, max_length=50)

    @field_validator("email")
    def validate_email(cls, v: str):
        if v is not None and not EMAIL_REGEX.match(v):
            raise ValueError("Invalid email format")
        return v

# -------- Outputs --------
class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str

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

