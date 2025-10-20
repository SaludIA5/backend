# app/databases/postgresql/models/__init__.py
from .base import BaseModel  # (opcional exportar)
from .diagnostic import Diagnostic
from .episode import Episode
from .episode_user import episode_user
from .patient import Patient
from .user import User
from .user_episodes_validations import UserEpisodeValidation

__all__ = [
    "BaseModel",
    "User",
    "Patient",
    "Episode",
    "Diagnostic",
    "UserEpisodeValidation",
    "episode_user",
]
