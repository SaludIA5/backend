from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MetricCreate(BaseModel):
    """Schema para crear métricas"""

    name: str = Field(..., description="Nombre de la métrica")
    description: Optional[str] = Field(None, description="Descripción de la métrica")
    value: float = Field(..., description="Valor de la métrica")
    metadata: Optional[dict] = Field(None, description="Metadatos adicionales")


class MetricOut(BaseModel):
    """Schema para mostrar métricas"""

    id: int
    name: str
    description: Optional[str]
    value: float
    metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MetricUpdate(BaseModel):
    """Schema para actualizar métricas"""

    name: Optional[str] = None
    description: Optional[str] = None
    value: Optional[float] = None
    metadata: Optional[dict] = None


class MetricPageMeta(BaseModel):
    """Metadata para paginación de métricas"""

    page: int
    page_size: int
    total: int
    total_pages: int


class MetricPage(BaseModel):
    """Schema para página de métricas"""

    items: list[MetricOut]
    meta: MetricPageMeta


# Esquemas específicos para métricas de recomendaciones de IA
class RecommendationMetrics(BaseModel):
    """Métricas de recomendaciones de IA"""

    total_recommendations: int = Field(
        ..., description="Total de recomendaciones generadas"
    )
    accepted_recommendations: int = Field(..., description="Recomendaciones aceptadas")
    rejected_recommendations: int = Field(..., description="Recomendaciones rechazadas")

    # Métricas de concordancia para aceptadas
    accepted_concordant: int = Field(
        ..., description="Aceptadas donde IA y médico coinciden"
    )
    accepted_ia_pertinent_doctor_pertinent: int = Field(
        ..., description="Aceptadas: IA PERTINENTE, Doctor PERTINENTE"
    )
    accepted_ia_no_pertinent_doctor_no_pertinent: int = Field(
        ..., description="Aceptadas: IA NO PERTINENTE, Doctor NO PERTINENTE"
    )

    # Métricas de discordancia para aceptadas
    accepted_discordant: int = Field(
        ..., description="Aceptadas donde IA y médico no coinciden"
    )
    accepted_ia_pertinent_doctor_no_pertinent: int = Field(
        ..., description="Aceptadas: IA PERTINENTE, Doctor NO PERTINENTE"
    )
    accepted_ia_no_pertinent_doctor_pertinent: int = Field(
        ..., description="Aceptadas: IA NO PERTINENTE, Doctor PERTINENTE"
    )

    # Métricas de concordancia para rechazadas
    rejected_concordant: int = Field(
        ..., description="Rechazadas donde IA y médico coinciden"
    )
    rejected_ia_pertinent_doctor_pertinent: int = Field(
        ..., description="Rechazadas: IA PERTINENTE, Doctor PERTINENTE"
    )
    rejected_ia_no_pertinent_doctor_no_pertinent: int = Field(
        ..., description="Rechazadas: IA NO PERTINENTE, Doctor NO PERTINENTE"
    )

    # Métricas de discordancia para rechazadas
    rejected_discordant: int = Field(
        ..., description="Rechazadas donde IA y médico no coinciden"
    )
    rejected_ia_pertinent_doctor_no_pertinent: int = Field(
        ..., description="Rechazadas: IA PERTINENTE, Doctor NO PERTINENTE"
    )
    rejected_ia_no_pertinent_doctor_pertinent: int = Field(
        ..., description="Rechazadas: IA NO PERTINENTE, Doctor PERTINENTE"
    )

    # Métricas de precisión
    precision: float = Field(..., description="Precisión de la IA")
    recall: float = Field(..., description="Recall de la IA")
    f1_score: float = Field(..., description="F1 Score de la IA")
    accuracy: float = Field(..., description="Exactitud de la IA")

    # Métricas adicionales
    concordance_rate: float = Field(..., description="Tasa de concordancia general")
    acceptance_rate: float = Field(..., description="Tasa de aceptación")


class ValidationMetrics(BaseModel):
    """Métricas de validaciones por médico"""

    doctor_id: int
    doctor_name: str
    total_validations: int
    accepted_validations: int
    rejected_validations: int
    concordant_validations: int
    discordant_validations: int
    concordance_rate: float
    acceptance_rate: float


class EpisodeMetrics(BaseModel):
    """Métricas por episodio"""

    episode_id: int
    numero_episodio: str
    patient_id: int
    ai_recommendation: str
    doctor_validation: str
    chief_validation: Optional[str]
    is_concordant: bool
    is_accepted: bool
    validation_date: Optional[datetime]
    validated_by_doctor: Optional[str]


class MetricsSummary(BaseModel):
    """Resumen general de métricas"""

    recommendation_metrics: RecommendationMetrics
    validation_metrics: list[ValidationMetrics]
    total_episodes: int
    episodes_with_ai_recommendation: int
    episodes_with_doctor_validation: int
    episodes_with_chief_validation: int
    period_start: Optional[datetime]
    period_end: Optional[datetime]
