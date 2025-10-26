from typing import List, Optional
from app.schemas.episode import EpisodeOut
from app.schemas.user import UserOut

class EpisodeWithDoctor(EpisodeOut):
    validator_doctors: List[UserOut] = []
