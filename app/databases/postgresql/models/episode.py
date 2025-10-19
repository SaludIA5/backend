# Tabla de asociación muchos-a-muchos
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
)
from sqlalchemy.orm import relationship
from .base import BaseModel

episode_diagnostic = Table(
    "episode_diagnostic",
    BaseModel.metadata,
    Column(
        "episode_id",
        Integer,
        ForeignKey("episodes.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "diagnostic_id",
        Integer,
        ForeignKey("diagnostics.id", ondelete="RESTRICT"),
        primary_key=True,
    ),
)


class Episode(BaseModel):
    __tablename__ = "episodes"

    patient_id = Column(
        Integer,
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    numero_episodio = Column(String(50), nullable=False, unique=True, index=True)
    fecha_estabilizacion = Column(Date)
    fecha_alta = Column(Date)
    validacion = Column(String(50))
    tipo = Column(String(50))
    tipo_alerta_ugcc = Column(String(100))
    fecha_ingreso = Column(Date)
    mes_ingreso = Column(Integer)
    fecha_egreso = Column(Date)
    mes_egreso = Column(Integer)
    centro = Column(String(100))
    antecedentes_cardiaco = Column(Boolean)
    antecedentes_diabetes = Column(Boolean)
    antecedentes_hipertension = Column(Boolean)
    triage = Column(Numeric(5, 2))
    presion_sistolica = Column(Numeric(5, 2))
    presion_diastolica = Column(Numeric(5, 2))
    presion_media = Column(Numeric(5, 2))
    temperatura_c = Column(Numeric(4, 1))
    saturacion_o2 = Column(Numeric(4, 1))
    frecuencia_cardiaca = Column(Numeric(5, 2))
    frecuencia_respiratoria = Column(Numeric(5, 2))
    tipo_cama = Column(String(50))
    glasgow_score = Column(Numeric(5, 2))
    fio2 = Column(Numeric(4, 1))
    fio2_ge_50 = Column(Boolean)
    ventilacion_mecanica = Column(Boolean)
    cirugia_realizada = Column(Boolean)
    cirugia_mismo_dia_ingreso = Column(Boolean)
    hemodinamia = Column(Boolean)
    hemodinamia_mismo_dia_ingreso = Column(Boolean)
    endoscopia = Column(Boolean)
    endoscopia_mismo_dia_ingreso = Column(Boolean)
    dialisis = Column(Boolean)
    trombolisis = Column(Boolean)
    trombolisis_mismo_dia_ingreso = Column(Boolean)
    pcr = Column(Numeric(6, 2))
    hemoglobina = Column(Numeric(4, 1))
    creatinina = Column(Numeric(5, 2))
    nitrogeno_ureico = Column(Numeric(5, 2))
    sodio = Column(Numeric(5, 2))
    potasio = Column(Numeric(4, 2))
    dreo = Column(Boolean)
    troponinas_alteradas = Column(Boolean)
    ecg_alterado = Column(Boolean)
    rnm_protocolo_stroke = Column(Boolean)
    dva = Column(Boolean)
    transfusiones = Column(Boolean)
    compromiso_conciencia = Column(Boolean)
    estado_del_caso = Column(String(50))
    recomendacion_modelo = Column(String(50))

    # Relación muchos-a-muchos
    diagnostics = relationship(
        "Diagnostic", secondary=episode_diagnostic, backref="episodes"
    )

    patient = relationship("Patient", back_populates="episodes")

    validated_by = relationship(
        "app.databases.postgresql.models.user_episodes_validations.UserEpisodeValidation",
        back_populates="episode",
        uselist=False,  # 1:1 relación hacia la validación
        cascade="all, delete-orphan"
    )
