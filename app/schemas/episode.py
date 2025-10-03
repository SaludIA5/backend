from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


# Un “lite” para mostrar diagnosticos asociados en la salida
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
    fecha_ingreso: Optional[date] = None
    fecha_estabilizacion: Optional[date] = None
    fecha_alta: Optional[date] = None
    validacion: Optional[str] = None
    tipo: Optional[str] = None
    tipo_alerta_ugcc: Optional[str] = None
    mes_ingreso: Optional[int] = None
    fecha_egreso: Optional[date] = None
    mes_egreso: Optional[int] = None
    centro: Optional[str] = None
    antecedentes_cardiaco: Optional[bool] = None
    antecedentes_diabetes: Optional[bool] = None
    antecedentes_hipertension: Optional[bool] = None
    triage: Optional[str] = None
    presion_sistolica: Optional[int] = None
    presion_diastolica: Optional[int] = None
    presion_media: Optional[int] = None
    temperatura_c: Optional[float] = None
    saturacion_o2: Optional[float] = None
    frecuencia_cardiaca: Optional[int] = None
    frecuencia_respiratoria: Optional[int] = None
    tipo_cama: Optional[str] = None
    glasgow_score: Optional[int] = None
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
    dreo: Optional[str] = None
    troponinas_alteradas: Optional[bool] = None
    ecg_alterado: Optional[bool] = None
    rnm_protocolo_stroke: Optional[bool] = None
    dva: Optional[bool] = None
    transfusiones: Optional[bool] = None
    compromiso_conciencia: Optional[bool] = None
    estado_del_caso: Optional[str] = None

    # IDs de diagnósticos para asociar (muchos-a-muchos)
    diagnostics_ids: Optional[List[int]] = None


class EpisodeUpdate(BaseModel):
    # todos opcionales: update parcial (PATCH)
    patient_id: Optional[int] = None
    numero_episodio: Optional[str] = Field(None, min_length=1, max_length=50)
    fecha_ingreso: Optional[date] = None
    fecha_estabilizacion: Optional[date] = None
    fecha_alta: Optional[date] = None
    validacion: Optional[str] = None
    tipo: Optional[str] = None
    tipo_alerta_ugcc: Optional[str] = None
    mes_ingreso: Optional[int] = None
    fecha_egreso: Optional[date] = None
    mes_egreso: Optional[int] = None
    centro: Optional[str] = None
    antecedentes_cardiaco: Optional[bool] = None
    antecedentes_diabetes: Optional[bool] = None
    antecedentes_hipertension: Optional[bool] = None
    triage: Optional[str] = None
    presion_sistolica: Optional[int] = None
    presion_diastolica: Optional[int] = None
    presion_media: Optional[int] = None
    temperatura_c: Optional[float] = None
    saturacion_o2: Optional[float] = None
    frecuencia_cardiaca: Optional[int] = None
    frecuencia_respiratoria: Optional[int] = None
    tipo_cama: Optional[str] = None
    glasgow_score: Optional[int] = None
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
    dreo: Optional[str] = None
    troponinas_alteradas: Optional[bool] = None
    ecg_alterado: Optional[bool] = None
    rnm_protocolo_stroke: Optional[bool] = None
    dva: Optional[bool] = None
    transfusiones: Optional[bool] = None
    compromiso_conciencia: Optional[bool] = None
    estado_del_caso: Optional[str] = None

    diagnostics_ids: Optional[List[int]] = None


# -------- Outputs --------
class EpisodeOut(BaseModel):
    id: int
    patient_id: int
    numero_episodio: str
    # muestra algunos campos clave y la lista de diagnósticos
    fecha_ingreso: Optional[date] = None
    fecha_egreso: Optional[date] = None
    estado_del_caso: Optional[str] = None
    diagnostics: List[DiagnosticLite] = Field(default_factory=list)

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
