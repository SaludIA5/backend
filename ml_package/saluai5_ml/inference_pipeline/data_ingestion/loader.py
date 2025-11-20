from decimal import Decimal
from typing import Any, Dict, List

import pandas as pd
import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.databases.postgresql.models import Diagnostic, Episode


class DataLoader:

    column_names = [
        "id_episodio",
        "validacion",
        "tipo",
        "tipo_alerta_ugcc",
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
    ]

    def __init__(self, session: AsyncSession):
        """
        Inicializa DataLoader con una sesión de base de datos.

        Args:
            session: AsyncSession de SQLAlchemy para acceder a la BD.
        """
        self.session = session

    def _get_attr_safe(self, obj: Any, name: str) -> Any:
        """Intentar obtener atributo con variantes comunes; devuelve None si no existe."""
        if hasattr(obj, name):
            return getattr(obj, name)
        if name == "id_episodio":
            for alt in ("id_episodio", "id", "numero_episodio", "numero"):
                if hasattr(obj, alt):
                    return getattr(obj, alt)
        return None

    async def fetch_all_episodes(self) -> List[Dict[str, Any]]:
        """
        Extrae episodios con validacion IS NOT NULL y devuelve lista de dicts
        con las columnas solicitadas + campo 'diagnostics' con lista de cie_code.
        """

        valid_col = getattr(Episode, "validacion", None)
        if valid_col is None:
            return []

        stmt = select(Episode).where(valid_col.is_not(None))
        result = await self.session.execute(stmt)
        episodes = result.scalars().all()

        if not episodes:
            return []

        episode_ids = self._extract_episode_ids(episodes)

        diagnostics_map = await self._fetch_diagnostics_map(episode_ids)

        out: List[Dict[str, Any]] = []
        for ep in episodes:
            row: Dict[str, Any] = {}
            for col in self.column_names:
                val = self._get_attr_safe(ep, col)
                if isinstance(val, Decimal):
                    val = float(val)
                row[col] = val

            eid = self._get_attr_safe(ep, "id_episodio") or getattr(ep, "id", None)
            row["diagnostics"] = diagnostics_map.get(eid, [])
            out.append(row)
        return out

    def _extract_episode_ids(self, episodes: List[Episode]) -> List[int]:
        """Extrae los IDs de los episodios."""
        episode_ids = []
        for ep in episodes:
            eid = self._get_attr_safe(ep, "id_episodio") or getattr(ep, "id", None)
            if eid is not None:
                try:
                    episode_ids.append(int(eid))
                except (ValueError, TypeError):
                    episode_ids.append(eid)
        return episode_ids

    async def _fetch_diagnostics_map(
        self, episode_ids: List[int]
    ) -> Dict[Any, List[str]]:
        """
        Obtiene los diagnosticos asociados a cada episodio.
        Devuelve un dict con episode_id como clave y lista de cie_codes como valor.
        """
        diagnostics_map: Dict[Any, List[str]] = {eid: [] for eid in episode_ids}

        if not episode_ids:
            return diagnostics_map

        metadata = Episode.__table__.metadata
        assoc_table = metadata.tables.get("episode_diagnostic")
        diag_table = Diagnostic.__table__

        if assoc_table is not None:
            sel = (
                sa.select(assoc_table.c.episode_id, diag_table.c.cie_code)
                .select_from(
                    assoc_table.join(
                        diag_table, assoc_table.c.diagnostic_id == diag_table.c.id
                    )
                )
                .where(assoc_table.c.episode_id.in_(episode_ids))
            )
            result = await self.session.execute(sel)
            for ep_id, cie_code in result.fetchall():
                if ep_id in diagnostics_map:
                    diagnostics_map[ep_id].append(cie_code)

        return diagnostics_map

    async def fetch_all_episodes_df(self) -> pd.DataFrame:
        """Devuelve los episodios como pandas DataFrame."""
        rows = await self.fetch_all_episodes()
        self.print_successful_operation(rows)
        return pd.DataFrame(rows)

    def print_successful_operation(self, data) -> None:
        """Imprime mensaje de exito"""
        print(f"✅ Datos cargados: {len(data)} filas")
