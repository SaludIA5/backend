from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_doctor: bool = False
    is_chief_doctor: bool = False
    is_admin: Optional[bool] = None
    user_id: int


class LoginRequest(BaseModel):
    email: str
    password: str
