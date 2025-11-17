"""Schemas for prediction endpoints."""

from typing import Literal, Optional, List

from pydantic import BaseModel, Field


class InferenceRequest(BaseModel):
    """Request schema for episode prediction."""

    # Model selection
    model_type: Literal["random_forest", "xgboost"] = Field(
        default="random_forest", description="Type of ML model to use for prediction"
    )

    id_episodio: Optional[int] = None
    numero_episodio: Optional[str] = None
    tipo: Optional[str] = None
    tipo_alerta_ugcc: Optional[str] = None
    diagnostics: Optional[List[str]] = None
    antecedentes_cardiaco: Optional[bool] = None
    antecedentes_diabetes: Optional[bool] = None
    antecedentes_hipertension: Optional[bool] = None
    triage: Optional[float] = None
    presion_sistolica: Optional[float] = None
    presion_diastolica: Optional[float] = None
    presion_media: Optional[float] = None
    temperatura_c: Optional[float] = None
    saturacion_o2: Optional[float] = None
    frecuencia_cardiaca: Optional[float] = None
    frecuencia_respiratoria: Optional[float] = None
    tipo_cama: Optional[str] = None
    glasgow_score: Optional[float] = None
    fio2: Optional[float] = None
    fio2_ge_50: Optional[bool] = None
    ventilacion_mecanica: Optional[bool] = None
    cirugia_realizada: Optional[bool] = None
    cirugia_mismo_dia_ingreso: Optional[bool] = None
    hemodinamia: Optional[bool] = None
    hemodinamia_mismo_dia_ingreso: Optional[bool] = None
    endoscopia: Optional[bool] = None
    endoscopia_mismo_dia_ingreso: Optional[bool] = None
    dialisis: Optional[bool] = None
    trombolisis: Optional[bool] = None
    trombolisis_mismo_dia_ingreso: Optional[bool] = None
    pcr: Optional[float] = None
    hemoglobina: Optional[float] = None
    creatinina: Optional[float] = None
    nitrogeno_ureico: Optional[float] = None
    sodio: Optional[float] = None
    potasio: Optional[float] = None
    model_type: Optional[str] = None
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
                "id_episodio": 0,
                "numero_episodio": "0",
                "diagnostics": None,
                "antecedentes_cardiaco": True,
                "antecedentes_diabetes": True,
                "antecedentes_hipertension": None,
                "creatinina": "50",
                "fio2": 0.5,
                "fio2_ge_50": None,
                "frecuencia_cardiaca": 150,
                "frecuencia_respiratoria": 150,
                "glasgow_score": 15,
                "hemoglobina": None,
                "model_type": "random_forest",
                "nitrogeno_ureico": None,
                "pcr": 80,
                "potasio": 8,
                "presion_diastolica": 50,
                "presion_media": 150,
                "presion_sistolica": 100,
                "saturacion_o2": 0.5,
                "sodio": 200,
                "temperatura_c": 25,
                "tipo": "SIN ALERTA",
                "tipo_alerta_ugcc": "SIN ALERTA",
                "tipo_cama": "Básica",
                "triage": 3,
                "ventilacion_mecanica": True,
                "cirugia_realizada": None,
                "cirugia_mismo_dia_ingreso": None,
                "hemodinamia": None,
                "hemodinamia_mismo_dia_ingreso": None,
                "endoscopia": True,
                "endoscopia_mismo_dia_ingreso": True,
                "dialisis": True,
                "trombolisis": None,
                "trombolisis_mismo_dia_ingreso": None,
                "dreo": None,
                "troponinas_alteradas": True,
                "ecg_alterado": True,
                "rnm_protocolo_stroke": True,
                "dva": None,
                "transfusiones": None,
                "compromiso_conciencia": True,
            }
        }


class InferenceResponse(BaseModel):
    """Response schema for episode inference."""

    inference: int = Field(
        ..., description="Inference class (0: NO PERTINENTE, 1: PERTINENTE)"
    )
    probability: float = Field(
        ..., ge=0.0, le=1.0, description="Inference probability/confidence"
    )
    label: str = Field(..., description="Human-readable label")
    model: str = Field(..., description="Model type used for inference")
    update_episode: Optional[str]

    class Config:
        json_schema_extra = {
            "example": {
                "prediction": 1,
                "probability": 0.87,
                "label": "PERTINENTE",
                "model": "random_forest",
                "update_episode": "Model recommendation added to the episode '0'",
            }
        }