"""Schemas for prediction endpoints."""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    """Request schema for episode prediction."""

    # Model selection
    model_type: Literal["random_forest", "xgboost"] = Field(
        default="xgboost", description="Type of ML model to use for prediction"
    )

    # Episode data
    tipo: Optional[str] = None
    tipo_alerta_ugcc: Optional[str] = None
    triage: Optional[int] = None

    # Antecedentes médicos
    antecedentes_cardiaco: Optional[bool] = None
    antecedentes_diabetes: Optional[bool] = None
    antecedentes_hipertension: Optional[bool] = None

    # Signos vitales
    presion_sistolica: Optional[float] = None
    presion_diastolica: Optional[float] = None
    presion_media: Optional[float] = None
    temperatura_c: Optional[float] = None
    saturacion_o2: Optional[float] = None
    frecuencia_cardiaca: Optional[float] = None
    frecuencia_respiratoria: Optional[float] = None

    # Scores y escalas
    glasgow_score: Optional[int] = None
    tipo_cama: Optional[str] = None

    # Soporte respiratorio
    fio2: Optional[float] = None
    fio2_ge_50: Optional[bool] = None
    ventilacion_mecanica: Optional[bool] = None

    # Procedimientos
    cirugia_realizada: Optional[bool] = None
    cirugia_mismo_dia_ingreso: Optional[bool] = None
    hemodinamia: Optional[bool] = None
    hemodinamia_mismo_dia_ingreso: Optional[bool] = None
    endoscopia: Optional[bool] = None
    endoscopia_mismo_dia_ingreso: Optional[bool] = None
    dialisis: Optional[bool] = None
    trombolisis: Optional[bool] = None
    trombolisis_mismo_dia_ingreso: Optional[bool] = None

    # Laboratorios
    pcr: Optional[float] = None
    hemoglobina: Optional[float] = None
    creatinina: Optional[float] = None
    nitrogeno_ureico: Optional[float] = None
    sodio: Optional[float] = None
    potasio: Optional[float] = None

    # Otros
    dreo: Optional[bool] = None
    troponinas_alteradas: Optional[bool] = None
    ecg_alterado: Optional[bool] = None
    rnm_protocolo_stroke: Optional[bool] = None
    dva: Optional[bool] = None
    transfusiones: Optional[bool] = None
    compromiso_conciencia: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "model_type": "xgboost",
                "tipo": "SIN ALERTA",
                "tipo_alerta_ugcc": "SIN ALERTA",
                "triage": 3,
                "antecedentes_cardiaco": True,
                "antecedentes_diabetes": False,
                "antecedentes_hipertension": True,
                "presion_sistolica": 160,
                "presion_diastolica": 95,
                "presion_media": 140,
                "temperatura_c": 36.5,
                "saturacion_o2": 97,
                "frecuencia_cardiaca": 104,
                "frecuencia_respiratoria": 27,
                "tipo_cama": "UCI",
                "glasgow_score": 14,
                "fio2": 0.21,
                "fio2_ge_50": False,
                "ventilacion_mecanica": False,
                "pcr": 17.51,
                "hemoglobina": 13.1,
                "creatinina": 0.92,
                "nitrogeno_ureico": 31,
                "sodio": 139,
                "potasio": 4.5,
            }
        }


class PredictionResponse(BaseModel):
    """Response schema for episode prediction."""

    prediction: int = Field(
        ..., description="Prediction class (0: NO PERTINENTE, 1: PERTINENTE)"
    )
    probability: float = Field(
        ..., ge=0.0, le=1.0, description="Prediction probability/confidence"
    )
    label: str = Field(..., description="Human-readable label")
    model: str = Field(..., description="Model type used for prediction")

    class Config:
        json_schema_extra = {
            "example": {
                "prediction": 1,
                "probability": 0.87,
                "label": "PERTINENTE",
                "model": "xgboost",
            }
        }
