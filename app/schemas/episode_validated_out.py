from typing import Optional
from pydantic import BaseModel
from app.schemas.episode import EpisodeOut
from app.schemas.user import UserOut

class EpisodeWithDoctor(EpisodeOut):
    doctor: Optional[UserOut] = None
