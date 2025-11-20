from pydantic import BaseModel


class TrainingRequest(BaseModel):
    stage: str = "dev"
