"""refactor_episode_and_add_recommendation

Revision ID: ed14b6831ae5
Revises: c56eb3b2ba66
Create Date: 2025-10-15 01:25:35.143462

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import Boolean, Date, Integer, Numeric, String

# revision identifiers, used by Alembic.
revision = "ed14b6831ae5"
down_revision = "c56eb3b2ba66"
branch_labels = None
depends_on = None

# Lista de columnas Integer a convertir a Numeric(5, 2)
INTEGER_COLS = [
    "presion_sistolica",
    "presion_diastolica",
    "presion_media",
    "frecuencia_cardiaca",
    "frecuencia_respiratoria",
    "glasgow_score",
]


def upgrade():
    # 1. ADD: Agregar la nueva columna 'recomendacion_modelo'
    op.add_column(
        "episodes", sa.Column("recomendacion_modelo", sa.String(50), nullable=True)
    )

    # 2. Eliminar la columna duplicada 'fecha_ingreso'
    # Nota: Asumimos que esta columna duplicada existe en la BD
    op.drop_column("episodes", "fecha_ingreso")

    # 3. Conversión de columnas Integer a Numeric(5, 2)
    for col_name in INTEGER_COLS:
        # Mantener la restricción NOT NULL solo para patient_id
        is_nullable = True if col_name != "patient_id" else False

        op.alter_column(
            "episodes",
            col_name,
            existing_type=Integer,
            type_=Numeric(5, 2),
            nullable=is_nullable,
            postgresql_using=f"CAST({col_name} AS NUMERIC(5, 2))",
        )

    # 4. Convertir 'triage' (String) a Numeric(5, 2)
    op.alter_column(
        "episodes",
        "triage",
        existing_type=String(50),
        type_=Numeric(5, 2),
        existing_nullable=True,
        postgresql_using="CAST(triage AS NUMERIC(5, 2))",
    )

    # 5. Convertir 'dreo' (String) a Boolean
    op.alter_column(
        "episodes",
        "dreo",
        existing_type=String(50),
        type_=Boolean,
        existing_nullable=True,
        postgresql_using="CASE WHEN dreo IN ('Si', 'si') THEN TRUE WHEN dreo IN ('No', 'no') THEN FALSE ELSE NULL END",
    )


def downgrade():
    # 1. DROP: Eliminar la columna 'recomendacion_modelo'
    op.drop_column("episodes", "recomendacion_modelo")

    # 2. Revertir 'dreo' a String(50)
    op.alter_column(
        "episodes",
        "dreo",
        existing_type=Boolean,
        type_=String(50),
        existing_nullable=True,
        postgresql_using="CASE WHEN dreo IS TRUE THEN 'Si' WHEN dreo IS FALSE THEN 'No' ELSE NULL END",
    )

    # 3. Revertir 'triage' a String(50)
    op.alter_column(
        "episodes",
        "triage",
        existing_type=Numeric(5, 2),
        type_=String(50),
        existing_nullable=True,
        postgresql_using="CAST(triage AS VARCHAR(50))",
    )

    # 4. Revertir Numeric a Integer (cuidado con la pérdida de datos)
    for col_name in INTEGER_COLS:
        is_nullable = True if col_name != "patient_id" else False
        op.alter_column(
            "episodes",
            col_name,
            existing_type=Numeric(5, 2),
            type_=Integer,
            nullable=is_nullable,
            postgresql_using=f"TRUNC({col_name})",  # Usamos TRUNC para convertir a entero de forma segura
        )

    # 5. ADD: Añadir la columna 'fecha_ingreso' eliminada
    op.add_column("episodes", sa.Column("fecha_ingreso", sa.Date(), nullable=True))
