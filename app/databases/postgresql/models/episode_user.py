from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Table,
)

from .base import BaseModel

# from sqlalchemy.orm import relationship <--- Ya no es necesario aquí


# Tabla de asociación Muchos-a-Muchos para asignar usuarios a episodios
episode_user = Table(
    "episode_user",  # Nombre de la tabla
    BaseModel.metadata,
    Column(
        "episode_id",
        Integer,
        ForeignKey("episodes.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "user_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    # Las columnas de asociación N:N no deben tener 'unique=True' a menos que sea una relación 1:N
)
