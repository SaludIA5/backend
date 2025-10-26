from typing import List
from pydantic import Field
from app.schemas.episode import EpisodeOut
from app.schemas.user import UserOut

class EpisodeWithTeamAndDoctor(EpisodeOut):
    assigned_doctors: List[UserOut] = Field(default_factory=list)
    validator_doctors: List[UserOut] = Field(default_factory=list)