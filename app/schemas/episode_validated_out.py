from typing import List

from app.schemas.episode import EpisodeOut
from app.schemas.user import UserOut


class EpisodeWithDoctor(EpisodeOut):
    validator_doctors: List[UserOut] = []
