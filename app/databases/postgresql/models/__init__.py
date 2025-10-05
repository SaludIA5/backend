# app/databases/postgresql/models/__init__.py
from .base import BaseModel  # (opcional exportar)
from .diagnostic import Diagnostic
from .episode import Episode
from .patient import Patient
from .user import User

__all__ = ["BaseModel", "User", "Patient", "Episode", "Diagnostic"]
