"""fill_episodes_diagnostics_table

Revision ID: ff23329b6cf4
Revises: db967178fe8f
Create Date: 2025-10-18 21:40:02.964603

"""

import ast
from pathlib import Path
from typing import Sequence, Union

import pandas as pd
import sqlalchemy as sa
from alembic import op
from sqlalchemy.orm import Session

# revision identifiers, used by Alembic.
revision: str = "ff23329b6cf4"
down_revision: Union[str, Sequence[str], None] = "db967178fe8f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

BASE_PATH = Path(__file__).resolve().parent.parent.parent


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    session = Session(bind=bind)

    CSV_PATH_EPISODES_DIAGNOSTICS = (
        BASE_PATH
        / "databases"
        / "postgresql"
        / "seeds"
        / "data"
        / "episodes_diagnostics.csv"
    )
    df = pd.read_csv(CSV_PATH_EPISODES_DIAGNOSTICS, dtype={"numero_episodio": str})

    if not {"numero_episodio", "codigos"}.issubset(df.columns):
        raise ValueError(
            "El CSV debe tener las columnas 'numero_episodio' y 'codigos'."
        )

    # Convertir string de lista a lista real
    import ast

    df["codigos"] = df["codigos"].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else x
    )

    episodes_map = {
        e.numero_episodio: e.id
        for e in session.execute(
            sa.select(
                sa.table("episodes", sa.column("id"), sa.column("numero_episodio"))
            )
        ).all()
    }
    diagnostics_map = {
        d.cie_code: d.id
        for d in session.execute(
            sa.select(sa.table("diagnostics", sa.column("id"), sa.column("cie_code")))
        ).all()
    }

    episode_diagnostic_table = sa.table(
        "episode_diagnostic",
        sa.column("episode_id", sa.Integer),
        sa.column("diagnostic_id", sa.Integer),
    )

    data_to_insert = []
    for _, row in df.iterrows():
        ep_num = row["numero_episodio"]
        ep_id = episodes_map.get(ep_num)
        if not ep_id:
            print(f"Episodio {ep_num} no encontrado, se salta.")
            continue

        for codigo in row["codigos"]:
            diag_id = diagnostics_map.get(codigo.strip())
            if not diag_id:
                print(f"Diagnostic {codigo} no encontrado, se salta.")
                continue

            data_to_insert.append({"episode_id": ep_id, "diagnostic_id": diag_id})

    if data_to_insert:
        op.bulk_insert(episode_diagnostic_table, data_to_insert)
        print(f"Se insertaron {len(data_to_insert)} relaciones en episode_diagnostic")


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    session = Session(bind=bind)

    CSV_PATH_EPISODES_DIAGNOSTICS = (
        BASE_PATH
        / "databases"
        / "postgresql"
        / "seeds"
        / "data"
        / "episodes_diagnostics.csv"
    )
    df = pd.read_csv(CSV_PATH_EPISODES_DIAGNOSTICS, dtype={"numero_episodio": str})

    if not {"numero_episodio", "codigos"}.issubset(df.columns):
        raise ValueError(
            "El CSV debe tener las columnas 'numero_episodio' y 'codigos'."
        )

    df["codigos"] = df["codigos"].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else x
    )

    episodes_map = {
        e.numero_episodio: e.id
        for e in session.execute(
            sa.select(
                sa.table("episodes", sa.column("id"), sa.column("numero_episodio"))
            )
        ).all()
    }
    diagnostics_map = {
        d.cie_code: d.id
        for d in session.execute(
            sa.select(sa.table("diagnostics", sa.column("id"), sa.column("cie_code")))
        ).all()
    }

    ids_to_delete = []
    for _, row in df.iterrows():
        ep_id = episodes_map.get(row["numero_episodio"])
        if not ep_id:
            continue

        for codigo in row["codigos"]:
            diag_id = diagnostics_map.get(codigo.strip())
            if not diag_id:
                continue
            ids_to_delete.append({"episode_id": ep_id, "diagnostic_id": diag_id})

    if ids_to_delete:
        episode_diagnostic_table = sa.table(
            "episode_diagnostic",
            sa.column("episode_id", sa.Integer),
            sa.column("diagnostic_id", sa.Integer),
        )

        for pair in ids_to_delete:
            delete_stmt = episode_diagnostic_table.delete().where(
                (episode_diagnostic_table.c.episode_id == pair["episode_id"])
                & (episode_diagnostic_table.c.diagnostic_id == pair["diagnostic_id"])
            )
            bind.execute(delete_stmt)

        print(f"Se eliminaron {len(ids_to_delete)} relaciones de episode_diagnostic")
