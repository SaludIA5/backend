from datetime import date
from decimal import Decimal
from typing import Any, List, Optional

from pydantic import BaseModel, BeforeValidator, Field
from typing_extensions import Annotated


def validate_numeric(value: Any) -> Optional[Decimal]:
    """Convierte un valor (incluyendo el objeto Numeric de SQLAlchemy) a Decimal o None."""
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except Exception:
        return None


PydanticDecimal = Annotated[Optional[Decimal], BeforeValidator(validate_numeric)]


class DiagnosticLite(BaseModel):
    id: int
    cie_code: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


# -------- Inputs --------
class EpisodeCreate(BaseModel):
    patient_id: int
    numero_episodio: str = Field(..., min_length=1, max_length=50)
    # campos opcionales (agrega los que uses con más frecuencia)
    fecha_estabilizacion: Optional[date] = None
    fecha_alta: Optional[date] = None
    validacion: Optional[str] = None
    tipo: Optional[str] = None
    tipo_alerta_ugcc: Optional[str] = None
    fecha_ingreso: Optional[date] = None
    mes_ingreso: Optional[int] = None
    fecha_egreso: Optional[date] = None
    mes_egreso: Optional[int] = None
    centro: Optional[str] = None
    antecedentes_cardiaco: Optional[bool] = None
    antecedentes_diabetes: Optional[bool] = None
    antecedentes_hipertension: Optional[bool] = None
    triage: Optional[PydanticDecimal] = None
    presion_sistolica: Optional[PydanticDecimal] = None
    presion_diastolica: Optional[PydanticDecimal] = None
    presion_media: Optional[PydanticDecimal] = None
    temperatura_c: Optional[PydanticDecimal] = None
    saturacion_o2: Optional[PydanticDecimal] = None
    frecuencia_cardiaca: Optional[PydanticDecimal] = None
    frecuencia_respiratoria: Optional[PydanticDecimal] = None
    tipo_cama: Optional[str] = None
    glasgow_score: Optional[PydanticDecimal] = None
    fio2: Optional[PydanticDecimal] = None
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
    pcr: Optional[PydanticDecimal] = None
    hemoglobina: Optional[PydanticDecimal] = None
    creatinina: Optional[PydanticDecimal] = None
    nitrogeno_ureico: Optional[PydanticDecimal] = None
    sodio: Optional[PydanticDecimal] = None
    potasio: Optional[PydanticDecimal] = None
    dreo: Optional[bool] = None
    troponinas_alteradas: Optional[bool] = None
    ecg_alterado: Optional[bool] = None
    rnm_protocolo_stroke: Optional[bool] = None
    dva: Optional[bool] = None
    transfusiones: Optional[bool] = None
    compromiso_conciencia: Optional[bool] = None
    estado_del_caso: Optional[str] = None
    recomendacion_modelo: Optional[str] = None
    validacion_jefe_turno: Optional[str] = None

    # IDs de diagnósticos para asociar (muchos-a-muchos)
    diagnostics_ids: Optional[List[int]] = None


class EpisodeUpdate(BaseModel):
    # todos opcionales: update parcial (PATCH)
    patient_id: Optional[int] = None
    numero_episodio: Optional[str] = Field(None, min_length=1, max_length=50)
    fecha_estabilizacion: Optional[date] = None
    fecha_alta: Optional[date] = None
    validacion: Optional[str] = None
    tipo: Optional[str] = None
    tipo_alerta_ugcc: Optional[str] = None
    fecha_ingreso: Optional[date] = None
    mes_ingreso: Optional[int] = None
    fecha_egreso: Optional[date] = None
    mes_egreso: Optional[int] = None
    centro: Optional[str] = None
    antecedentes_cardiaco: Optional[bool] = None
    antecedentes_diabetes: Optional[bool] = None
    antecedentes_hipertension: Optional[bool] = None
    triage: Optional[PydanticDecimal] = None
    presion_sistolica: Optional[PydanticDecimal] = None
    presion_diastolica: Optional[PydanticDecimal] = None
    presion_media: Optional[PydanticDecimal] = None
    temperatura_c: Optional[PydanticDecimal] = None
    saturacion_o2: Optional[PydanticDecimal] = None
    frecuencia_cardiaca: Optional[PydanticDecimal] = None
    frecuencia_respiratoria: Optional[PydanticDecimal] = None
    tipo_cama: Optional[str] = None
    glasgow_score: Optional[PydanticDecimal] = None
    fio2: Optional[PydanticDecimal] = None
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
    pcr: Optional[PydanticDecimal] = None
    hemoglobina: Optional[PydanticDecimal] = None
    creatinina: Optional[PydanticDecimal] = None
    nitrogeno_ureico: Optional[PydanticDecimal] = None
    sodio: Optional[PydanticDecimal] = None
    potasio: Optional[PydanticDecimal] = None
    dreo: Optional[bool] = None
    troponinas_alteradas: Optional[bool] = None
    ecg_alterado: Optional[bool] = None
    rnm_protocolo_stroke: Optional[bool] = None
    dva: Optional[bool] = None
    transfusiones: Optional[bool] = None
    compromiso_conciencia: Optional[bool] = None
    estado_del_caso: Optional[str] = None
    recomendacion_modelo: Optional[str] = None
    validacion_jefe_turno: Optional[str] = None

    diagnostics_ids: Optional[List[int]] = None


# -------- Outputs --------
class EpisodeOut(BaseModel):
    # id: int
    # patient_id: int
    # numero_episodio: str
    # # muestra algunos campos clave y la lista de diagnósticos
    # fecha_ingreso: Optional[date] = None
    # fecha_egreso: Optional[date] = None
    # estado_del_caso: Optional[str] = None
    # diagnostics: List[DiagnosticLite] = Field(default_factory=list)

    id: int
    patient_id: int
    numero_episodio: str = Field(..., min_length=1, max_length=50)
    # campos opcionales (agrega los que uses con más frecuencia)
    fecha_estabilizacion: Optional[date] = None
    fecha_alta: Optional[date] = None
    validacion: Optional[str] = None
    tipo: Optional[str] = None
    tipo_alerta_ugcc: Optional[str] = None
    fecha_ingreso: Optional[date] = None
    mes_ingreso: Optional[int] = None
    fecha_egreso: Optional[date] = None
    mes_egreso: Optional[int] = None
    centro: Optional[str] = None
    antecedentes_cardiaco: Optional[bool] = None
    antecedentes_diabetes: Optional[bool] = None
    antecedentes_hipertension: Optional[bool] = None
    triage: Optional[PydanticDecimal] = None
    presion_sistolica: Optional[PydanticDecimal] = None
    presion_diastolica: Optional[PydanticDecimal] = None
    presion_media: Optional[PydanticDecimal] = None
    temperatura_c: Optional[PydanticDecimal] = None
    saturacion_o2: Optional[PydanticDecimal] = None
    frecuencia_cardiaca: Optional[PydanticDecimal] = None
    frecuencia_respiratoria: Optional[PydanticDecimal] = None
    tipo_cama: Optional[str] = None
    glasgow_score: Optional[PydanticDecimal] = None
    fio2: Optional[PydanticDecimal] = None
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
    pcr: Optional[PydanticDecimal] = None
    hemoglobina: Optional[PydanticDecimal] = None
    creatinina: Optional[PydanticDecimal] = None
    nitrogeno_ureico: Optional[PydanticDecimal] = None
    sodio: Optional[PydanticDecimal] = None
    potasio: Optional[PydanticDecimal] = None
    dreo: Optional[bool] = None
    troponinas_alteradas: Optional[bool] = None
    ecg_alterado: Optional[bool] = None
    rnm_protocolo_stroke: Optional[bool] = None
    dva: Optional[bool] = None
    transfusiones: Optional[bool] = None
    compromiso_conciencia: Optional[bool] = None
    estado_del_caso: Optional[str] = None
    recomendacion_modelo: Optional[str] = None
    validacion_jefe_turno: Optional[str] = None

    # IDs de diagnósticos para asociar (muchos-a-muchos)
    diagnostics_ids: Optional[List[int]] = None

    class Config:
        from_attributes = True


class EpisodePageMeta(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int


class EpisodePage(BaseModel):
    items: List[EpisodeOut]
    meta: EpisodePageMeta
