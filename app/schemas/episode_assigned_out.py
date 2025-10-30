from typing import List

from app.schemas.episode import EpisodeOut
from app.schemas.user import UserOut


class EpisodeWithTeam(EpisodeOut):
    assigned_doctors: List[UserOut] = []
    patient_name: str | None = None
    patient_rut: str | None = None
    patient_age: int | None = None
