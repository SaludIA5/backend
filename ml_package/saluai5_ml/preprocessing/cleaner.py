from pathlib import Path

import numpy as np
import pandas as pd


def get_base_directory() -> Path:
    """Get the base directory of the package."""
    return Path(__file__).resolve().parent.parent


def read_excel_file(file_path: str, sheet: int = 0) -> pd.DataFrame:
    """
    Read an Excel file and return a DataFrame
    """
    df = pd.read_excel(file_path, sheet_name=sheet, engine="openpyxl")
    return df


def filter_valid_episodes(
    df: pd.DataFrame, column: str, values: list[str]
) -> pd.DataFrame:
    """
    Filter the data with a specific column and values.
    """
    df_filtered = df[df[column].isin(values)]
    return df_filtered


def drop_irrelevant_columns(
    df: pd.DataFrame,
    column_names: list[str],
) -> pd.DataFrame:
    """
    Drop the columns specified in values from the dataframe based on the column name.
    """
    return df.drop(columns=column_names, errors="ignore")


def rename_columns(df: pd.DataFrame, columns_map: dict) -> pd.DataFrame:
    """
    Rename columns in the dataframe based on the provided mapping.
    """
    return df.rename(columns=columns_map)


def encode_binary_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    Encode binary columns to 0 and 1.
    """
    df_copy = df.copy()
    for col in columns:
        if col in df_copy.columns:
            df_copy[col] = df_copy[col].apply(lambda x: map_binary_value(x))

    return df_copy


def map_binary_value(value):
    """
    Map to binary value.
    """
    if isinstance(value, str):
        # val = value.strip().lower()
        if value in ["Si", "Sí"]:
            return 1
        elif value == "No":
            return 0
    elif isinstance(value, bool):
        return 1 if value else 0

    return np.nan


def fill_nr_and_empty_numerical_columns(
    df: pd.DataFrame, columnas_a_rellenar
) -> pd.DataFrame:
    """
    Fill 'NR' and empty values in numerical columns with the mean of the respective columns.
    """
    medias_a_usar = {}
    for columna in columnas_a_rellenar:
        df[columna] = pd.to_numeric(df[columna], errors="coerce")
        media = df[columna].mean(skipna=True)
        medias_a_usar[columna] = media
    df_rellenado = df.fillna(medias_a_usar)

    return df_rellenado


def save_df_to_csv(df: pd.DataFrame, file_path: str, index: bool = False) -> None:
    """
    Save the DataFrame to a CSV file.
    """
    df.to_csv(file_path, index=index, encoding="utf-8", sep=";")


def data_cleaner(file_name: str, file_name_output: str) -> pd.DataFrame:
    """
    Preprocess the data.
    """
    base_directory = get_base_directory()
    file_path = base_directory / "data" / "raw" / file_name
    df = read_excel_file(str(file_path), sheet=0)
    df_filtered = filter_valid_episodes(
        df, "VALIDACIÓN", ["PERTINENTE", "NO PERTINENTE"]
    )
    df = drop_irrelevant_columns(
        df_filtered,
        [
            "Fecha Adm",
            "Fecha Est.",
            "Fecha Alta",
            "Fecha Ingreso",
            "Mes Ingreso",
            "Fecha Egreso",
            "Mes Egreso",
            "Centro",
            "Estado del caso",
            "Creado",
        ],
    )

    df = rename_columns(
        df,
        {
            "Episodio": "numero_episodio",
            "VALIDACIÓN": "validacion",
            "TIPO": "tipo",
            "CUAL ALERTA UGCC": "tipo_alerta_ugcc",
            "Diagnóstico": "diagnostics",
            "Antecedentes Cardíacos": "antecedentes_cardiaco",
            "Antecedentes Diabeticos": "antecedentes_diabetes",
            "Antecedentes de Hipertensión Arterial": "antecedentes_hipertension",
            "Triage": "triage",
            "Presión Arterial Sistólica": "presion_sistolica",
            "Presión Arterial Diastólica": "presion_diastolica",
            "Presión Arterial Media": "presion_media",
            "Temperatura en °C": "temperatura_c",
            "Saturación Oxígeno": "saturacion_o2",
            "Frecuencia Cardíaca": "frecuencia_cardiaca",
            "Frecuencia Respiratoria": "frecuencia_respiratoria",
            "Tipo de Cama": "tipo_cama",
            "Glasgow": "glasgow_score",
            "FIO2": "fio2",
            "FIO2 > o igual a 50%": "fio2_ge_50",
            "Ventilación Mecánica": "ventilacion_mecanica",
            "Cirugía Realizada": "cirugia_realizada",
            "Cirugía mismo día ingreso": "cirugia_mismo_dia_ingreso",
            "Hemodinamia Realizada": "hemodinamia",
            "Hemodinamia mismo dia ingreso": "hemodinamia_mismo_dia_ingreso",
            "Endoscopia": "endoscopia",
            "Endoscopia mismo día ingreso": "endoscopia_mismo_dia_ingreso",
            "Diálisis": "dialisis",
            "Trombólisis": "trombolisis",
            "Trombólisis mismo día ingreso": "trombolisis_mismo_dia_ingreso",
            "PCR": "pcr",
            "Hemoglobina": "hemoglobina",
            "Creatinina": "creatinina",
            "Nitrogeno Ureico": "nitrogeno_ureico",
            "Sodio": "sodio",
            "Potasio": "potasio",
            "Dreo": "dreo",
            "Troponinas Alteradas": "troponinas_alteradas",
            "ECG Alterado": "ecg_alterado",
            "RNM Protocolo Stroke": "rnm_protocolo_stroke",
            "DVA": "dva",
            "Transfusiones": "transfusiones",
            "Compromiso Conciencia": "compromiso_conciencia",
        },
    )

    # df = fill_nr_and_empty_numerical_columns(df, ["frecuencia_respiratoria", "pcr", "hemoglobina", "creatinina",
    #                                              "nitrogeno_ureico", "sodio", "potasio"])
    df = encode_binary_columns(
        df,
        [
            "antecedentes_cardiaco",
            "antecedentes_diabetes",
            "antecedentes_hipertension",
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
            "troponinas_alteradas",
            "ecg_alterado",
            "rnm_protocolo_stroke",
            "dva",
            "transfusiones",
            "compromiso_conciencia",
            "dreo",
        ],
    )

    output_file_path = base_directory / "data" / "processed" / file_name_output
    save_df_to_csv(df, str(output_file_path))


if __name__ == "__main__":
    data_cleaner("initial_data.xlsx", "initial_data_cleaned.csv")
