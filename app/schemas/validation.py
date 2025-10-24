from typing import Literal
from pydantic import BaseModel, Field

class ValidateEpisodeRequest(BaseModel):
    user_id: int = Field(..., ge=1, description="ID del doctor que valida")
    decision: Literal["PERTINENTE", "NO PERTINENTE"] = Field(
        ..., description='Decisión final: "PERTINENTE" o "NO PERTINENTE"'
    )