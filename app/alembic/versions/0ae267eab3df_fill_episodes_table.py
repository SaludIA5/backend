"""fill_episodes_table

Revision ID: 0ae267eab3df
Revises: 4d97e8a97167
Create Date: 2025-10-15 19:33:02.132270

"""


import random

from pathlib import Path
from typing import Sequence, Union

import numpy as np
import pandas as pd
import sqlalchemy as sa
from alembic import op
from sqlalchemy import Boolean, Date, Integer, Numeric, String
from sqlalchemy.orm import Session
from sqlalchemy.sql import column, select, table

revision: str = "0ae267eab3df"
# down_revision: Union[str, Sequence[str], None] = '4d97e8a97167'
down_revision: Union[str, Sequence[str], None] = "e7723e54e9b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

BASE_PATH = Path(__file__).resolve().parent.parent.parent


def define_episodes_table():
    return table(
        "episodes",
        column("patient_id", Integer),
        column("numero_episodio", String(50)),
        column("fecha_estabilizacion", Date),
        column("fecha_alta", Date),
        column("validacion", String(50)),
        column("tipo", String(50)),
        column("tipo_alerta_ugcc", String(100)),
        column("fecha_ingreso", Date),
        column("mes_ingreso", Integer),
        column("fecha_egreso", Date),
        column("mes_egreso", Integer),
        column("centro", String(100)),
        column("antecedentes_cardiaco", Boolean),
        column("antecedentes_diabetes", Boolean),
        column("antecedentes_hipertension", Boolean),
        column("triage", Numeric(5, 2)),
        column("presion_sistolica", Numeric(5, 2)),
        column("presion_diastolica", Numeric(5, 2)),
        column("presion_media", Numeric(5, 2)),
        column("temperatura_c", Numeric(4, 1)),
        column("saturacion_o2", Numeric(4, 1)),
        column("frecuencia_cardiaca", Numeric(5, 2)),
        column("frecuencia_respiratoria", Numeric(5, 2)),
        column("tipo_cama", String(50)),
        column("glasgow_score", Numeric(5, 2)),
        column("fio2", Numeric(4, 1)),
        column("fio2_ge_50", Boolean),
        column("ventilacion_mecanica", Boolean),
        column("cirugia_realizada", Boolean),
        column("cirugia_mismo_dia_ingreso", Boolean),
        column("hemodinamia", Boolean),
        column("hemodinamia_mismo_dia_ingreso", Boolean),
        column("endoscopia", Boolean),
        column("endoscopia_mismo_dia_ingreso", Boolean),
        column("dialisis", Boolean),
        column("trombolisis", Boolean),
        column("trombolisis_mismo_dia_ingreso", Boolean),
        column("pcr", Numeric(6, 2)),
        column("hemoglobina", Numeric(4, 1)),
        column("creatinina", Numeric(5, 2)),
        column("nitrogeno_ureico", Numeric(5, 2)),
        column("sodio", Numeric(5, 2)),
        column("potasio", Numeric(4, 2)),
        column("dreo", Boolean),
        column("troponinas_alteradas", Boolean),
        column("ecg_alterado", Boolean),
        column("rnm_protocolo_stroke", Boolean),
        column("dva", Boolean),
        column("transfusiones", Boolean),
        column("compromiso_conciencia", Boolean),
        column("estado_del_caso", String(50)),
        column("recomendacion_modelo", String(50)),
    )


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    episodes_table = define_episodes_table()

    patients_table = table("patients", column("id", Integer))
    patient_ids_result = session.execute(select(patients_table.c.id)).fetchall()
    patient_ids = [row[0] for row in patient_ids_result]

    assigned_ids = patient_ids.copy()
    random.shuffle(assigned_ids)

    CSV_PATH = (
        BASE_PATH / "databases" / "postgresql" / "seeds" / "data" / "episodes_data.csv"
    )
    df = pd.read_csv(CSV_PATH)
    df["patient_id"] = assigned_ids

    orden_columnas = [
        "patient_id",
        "numero_episodio",
        "fecha_estabilizacion",
        "fecha_alta",
        "validacion",
        "tipo",
        "tipo_alerta_ugcc",
        "fecha_ingreso",
        "mes_ingreso",
        "fecha_egreso",
        "mes_egreso",
        "centro",
        "antecedentes_cardiaco",
        "antecedentes_diabetes",
        "antecedentes_hipertension",
        "triage",
        "presion_sistolica",
        "presion_diastolica",
        "presion_media",
        "temperatura_c",
        "saturacion_o2",
        "frecuencia_cardiaca",
        "frecuencia_respiratoria",
        "tipo_cama",
        "glasgow_score",
        "fio2",
        "fio2_ge_50",
        "ventilacion_mecanica",
        "cirugia_realizada",
        "cirugia_mismo_dia_ingreso",
        "hemodinamia",
        "hemodinamia_mismo_dia_ingreso",
        "endoscopia",
        "endoscopia_mismo_dia_ingreso",
        "dialisis",
        "trombolisis",
        "trombolisis_mismo_dia_ingreso",
        "pcr",
        "hemoglobina",
        "creatinina",
        "nitrogeno_ureico",
        "sodio",
        "potasio",
        "dreo",
        "troponinas_alteradas",
        "ecg_alterado",
        "rnm_protocolo_stroke",
        "dva",
        "transfusiones",
        "compromiso_conciencia",
        "estado_del_caso",
        "recomendacion_modelo",
    ]

    df = df[orden_columnas]
    df["numero_episodio"] = df["numero_episodio"].astype(str)

    DATE_COLS = ["fecha_estabilizacion", "fecha_alta", "fecha_ingreso", "fecha_egreso"]
    for col in DATE_COLS:
        df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=False)
        df[col] = df[col].dt.date
        df[col] = df[col].apply(lambda x: x if pd.notna(x) else None)

    data_to_insert = df.to_dict(orient="records")
    op.bulk_insert(episodes_table, data_to_insert)
    session.commit()
    print(f"¡Carga masiva de {len(data_to_insert)} episodios completada")


def downgrade():
    try:
        CSV_PATH = (
            BASE_PATH
            / "databases"
            / "postgresql"
            / "seeds"
            / "data"
            / "episodes_data.csv"
        )
        df = pd.read_csv(CSV_PATH)
        df["numero_episodio"] = df["numero_episodio"].astype(str)
        df_downgrade = df
        episode_numbers_to_delete = df_downgrade["numero_episodio"].unique().tolist()
    except FileNotFoundError:
        print("No se puede revertir. Archivo CSV no encontrado.")
        return

    episodes_table = define_episodes_table()

    op.execute(
        episodes_table.delete().where(
            episodes_table.c.numero_episodio.in_(episode_numbers_to_delete)
        )
    )
    print(f"Reversión de {len(episode_numbers_to_delete)} episodios completada.")
