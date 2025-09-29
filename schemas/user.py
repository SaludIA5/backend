from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

# -------- Inputs --------
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=255)
    role: str = Field(default="Otro", min_length=1, max_length=50)

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, max_length=255)
    role: Optional[str] = Field(None, min_length=1, max_length=50)

# -------- Outputs --------
class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True

class PageMeta(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int

class UserPage(BaseModel):
    items: List[UserOut]
    meta: PageMeta
