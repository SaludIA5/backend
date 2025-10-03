# app/databases/postgresql/models/__init__.py
from .base import BaseModel  # (opcional exportar)
from .user import User
from .patient import Patient
from .episode import Episode
from .diagnostic import Diagnostic

__all__ = ["BaseModel", "User", "Patient", "Episode", "Diagnostic"]
