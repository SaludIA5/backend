"""fill_diagnostics_table

Revision ID: db967178fe8f
Revises: 32e0a7b83af2
Create Date: 2025-10-18 19:16:09.297629

"""

from pathlib import Path
from typing import Sequence, Union

import pandas as pd
import sqlalchemy as sa
from alembic import op
from sqlalchemy.orm import Session

# revision identifiers, used by Alembic.
revision: str = "db967178fe8f"
down_revision: Union[str, Sequence[str], None] = "32e0a7b83af2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

BASE_PATH = Path(__file__).resolve().parent.parent.parent


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    session = Session(bind=bind)
    CSV_PATH_DIAGNOSTICS = (
        BASE_PATH / "databases" / "postgresql" / "seeds" / "data" / "diagnostics.csv"
    )

    df = pd.read_csv(CSV_PATH_DIAGNOSTICS, sep=";")

    if not {"codigo", "descripcion"}.issubset(df.columns):
        raise ValueError("El CSV debe tener las columnas 'codigo' y 'descripcion'.")

    df = df.rename(columns={"codigo": "cie_code", "descripcion": "description"})
    data_to_insert = df[["cie_code", "description"]].to_dict(orient="records")
    diagnostics_table = sa.table(
        "diagnostics",
        sa.column("cie_code", sa.String),
        sa.column("description", sa.String),
    )

    op.bulk_insert(diagnostics_table, data_to_insert)
    session.commit()
    print(f"¡Carga masiva de {len(data_to_insert)} diagnosticos completada")


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    CSV_PATH_DIAGNOSTICS = (
        BASE_PATH / "databases" / "postgresql" / "seeds" / "data" / "diagnostics.csv"
    )

    df = pd.read_csv(CSV_PATH_DIAGNOSTICS, sep=";")

    if "codigo" not in df.columns:
        raise ValueError("El CSV debe tener la columna 'codigo' para el downgrade.")

    cie_codes = df["codigo"].dropna().tolist()

    if not cie_codes:
        return

    delete_stmt = sa.text("DELETE FROM diagnostics WHERE cie_code = ANY(:codes)")
    bind.execute(delete_stmt, {"codes": cie_codes})
