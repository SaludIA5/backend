from typing import Optional

from pydantic import BaseModel


# Definiciones Lite para evitar bucles de dependencia en la salida
# Deben estar definidas en tu proyecto (aquí son placeholders conceptuales)
class UserLite(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class EpisodeLite(BaseModel):
    id: int
    numero_episodio: str

    class Config:
        from_attributes = True


# ----------------- Inputs -----------------


class EpisodeUserCreate(BaseModel):
    """
    Esquema para crear un registro en la tabla 'episode_user'.
    Requiere las IDs de los dos objetos que se asocian.
    """

    # user_id: no nullable en SQL
    user_id: int

    # episode_id: no nullable y UNIQUE en SQL
    episode_id: int


class EpisodeUserUpdate(BaseModel):
    """
    Esquema para actualizar campos. Todos son opcionales.
    """

    user_id: Optional[int] = None
    episode_id: Optional[int] = None


# ----------------- Outputs -----------------


class EpisodeUserOut(BaseModel):
    """
    Esquema de salida para devolver el objeto de asociación.
    Incluye las claves foráneas y la representación 'Lite' de las relaciones.
    """

    # Campos base (asumiendo que BaseModel te proporciona 'id')
    id: int
    user_id: int
    episode_id: int
    # created_at: Optional[datetime] # Añadir si BaseModel tiene timestamps

    # Relaciones cargadas por SQLAlchemy
    # Usamos esquemas Lite para evitar cargar toda la jerarquía de User y Episode.
    user: UserLite
    episode: EpisodeLite

    class Config:
        from_attributes = True
