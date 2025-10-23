from typing import List
from app.schemas.episode import EpisodeOut
from app.schemas.user import UserOut

class EpisodeWithTeam(EpisodeOut):
    team: List[UserOut] = []
