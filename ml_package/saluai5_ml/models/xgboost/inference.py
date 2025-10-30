from pathlib import Path

import joblib
import pandas as pd
import saluai5_ml.models.utils as u

BINARY_COLUMNS = [
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
]
NUMERICAL_COLUMNS = [
    "presion_sistolica",
    "presion_diastolica",
    "presion_media",
    "temperatura_c",
    "saturacion_o2",
    "frecuencia_cardiaca",
    "frecuencia_respiratoria",
    "glasgow_score",
    "fio2",
    "pcr",
    "hemoglobina",
    "creatinina",
    "nitrogeno_ureico",
    "sodio",
    "potasio",
]
CATEGORICAL_COLUMNS = ["tipo", "tipo_alerta_ugcc", "tipo_cama", "triage"]
DIAGNOSTIC_COLUMN = "diagnostics"


def get_representative_values_colums() -> tuple:
    """
    Get representative values for numerical and categorical columns.
    """

    base_path = Path(__file__).resolve().parent.parent.parent
    data_cleaned_file_path = (
        base_path / "data" / "processed" / "initial_data_cleaned.csv"
    )
    df = pd.read_csv(data_cleaned_file_path, sep=";", encoding="utf-8")

    mean_nc = u.get_means_numerical_columns(df, NUMERICAL_COLUMNS)
    mode_cc = u.get_mode_categorical_columns(df, CATEGORICAL_COLUMNS)
    mode_bc = u.get_mode_binary_columns(df, BINARY_COLUMNS)
    diagnostic = u.get_random_value_from_column(df, DIAGNOSTIC_COLUMN)

    return (mean_nc, mode_cc, mode_bc, diagnostic)


def load_model(name_model: str) -> any:
    """
    Load the trained model from a file."""
    base_path = Path(__file__).resolve().parent
    model_path = base_path / name_model
    model = joblib.load(model_path)
    return model


def preprocess_form_data(form_data: dict) -> dict:
    """
    Preprocess the form data to match the model's expected input format.
    """

    for col in BINARY_COLUMNS:
        if col in form_data.keys():
            form_data[col] = (
                1
                if form_data[col]
                in [1, "1", True, "true", "True", "Sí", "si", "SI", "YES", "yes", "Yes"]
                else 0
            )

    for col in CATEGORICAL_COLUMNS:
        if col in form_data.keys():
            if col in ["tipo", "tipo_alerta_ugcc"]:
                form_data[col] = form_data[col].upper()

    for col in NUMERICAL_COLUMNS:
        if col in form_data.keys():
            try:
                form_data[col] = float(form_data[col])
            except (ValueError, TypeError):
                form_data[col] = None

    return form_data


def fill_missing_values(form_data: dict) -> dict:
    mean_nc, mode_cc, mode_bc, diagnostic = get_representative_values_colums()
    for col in NUMERICAL_COLUMNS:
        if col in form_data.keys():
            if form_data[col] in [None, "", "NR"]:
                form_data[col] = mean_nc[col]
    for col in CATEGORICAL_COLUMNS:
        if col in form_data.keys():
            if form_data[col] in [None, "", "NR"]:
                form_data[col] = mode_cc[col]

    for col in BINARY_COLUMNS:
        if col in form_data.keys():
            if form_data[col] in [None, "", "NR"]:
                form_data[col] = mode_bc[col]

    # form_data[DIAGNOSTIC_COLUMN] = form_data.get(DIAGNOSTIC_COLUMN, diagnostic)
    return form_data


def apply_encoders_to_columns(form_data: dict) -> any:
    """
    Apply the necessary encoders to the form data.
    """
    base_path = Path(__file__).resolve().parent.parent.parent
    ohe_path = base_path / "encoders" / "categorical_one_hot_encoder.pkl"
    base_path / "encoders" / "diagnostics_label_encoder.pkl"
    numerical_encoder_path = base_path / "encoders" / "numerical_min_max_scaler.pkl"
    ohe_encoder = joblib.load(ohe_path)
    # label_encoder = joblib.load(label_encoder_path)
    numerical_encoder = joblib.load(numerical_encoder_path)

    df_input = pd.DataFrame([form_data])

    # df_input["diagnostics_encoded"] = label_encoder.transform(df_input[DIAGNOSTIC_COLUMN])

    # cat_columns = CATEGORICAL_COLUMNS + ["diagnostics_encoded"]
    cat_columns = CATEGORICAL_COLUMNS
    df_input_encoded_categorical = ohe_encoder.transform(df_input[cat_columns])
    df_ohe = pd.DataFrame(
        df_input_encoded_categorical,
        columns=ohe_encoder.get_feature_names_out(cat_columns),
        index=df_input.index,
    )

    df_encoded = pd.concat([df_input.drop(columns=cat_columns), df_ohe], axis=1)

    df_encoded[NUMERICAL_COLUMNS] = numerical_encoder.transform(
        df_encoded[NUMERICAL_COLUMNS]
    )

    invalid_columns_to_inference = [
        "diagnostics",
        "numero_episodio",
        "validacion",
    ] + cat_columns
    valid_columns_to_inference = [
        col for col in df_encoded.columns if col not in invalid_columns_to_inference
    ]

    df_filtered = df_encoded[valid_columns_to_inference]
    return df_filtered


def get_model_prediction(model: any, df: pd.DataFrame) -> dict:
    """
    Get the model's prediction and probability.
    """
    label_prediction = model.predict(df)[0]
    label_prediction_proba_np = model.predict_proba(df)[0]
    label_prob = round(float(label_prediction_proba_np[int(label_prediction)]), 2)

    return {"prediction": int(label_prediction), "probability": label_prob}


def make_prediction(form_data: dict) -> dict:
    """
    Make a prediction using the trained model.
    """

    preprocessed_form = preprocess_form_data(form_data)
    completed_form = fill_missing_values(preprocessed_form)
    df_encoded = apply_encoders_to_columns(completed_form)
    rf_model = load_model("xgboost_model.pkl")
    return get_model_prediction(rf_model, df_encoded)


if __name__ == "__main__":
    form_data = {
        "numero_episodio": 0,
        "validacion": 1,
        "tipo": "SIN ALERTA",
        "tipo_alerta_ugcc": "SIN ALERTA",
        "diagnostics": "N19-INSUFICIENCIA RENAL NO ESPECIFICADA ",
        "antecedentes_cardiaco": "Sí",
        "antecedentes_diabetes": "No",
        "antecedentes_hipertension": "Sí",
        "triage": 3,
        "presion_sistolica": 160,
        "presion_diastolica": 95,
        "presion_media": 140,
        "temperatura_c": 36.5,
        "saturacion_o2": 97,
        "frecuencia_cardiaca": 104,
        "frecuencia_respiratoria": 27,
        "tipo_cama": "UCI",
        "glasgow_score": 14,
        "fio2": 0.21,
        "fio2_ge_50": "No",
        "ventilacion_mecanica": "No",
        "cirugia_realizada": "No",
        "cirugia_mismo_dia_ingreso": "No",
        "hemodinamia": "No",
        "hemodinamia_mismo_dia_ingreso": "No",
        "endoscopia": "No",
        "endoscopia_mismo_dia_ingreso": "No",
        "dialisis": "No",
        "trombolisis": "No",
        "trombolisis_mismo_dia_ingreso": "No",
        "pcr": 17.51,
        "hemoglobina": 13.1,
        "creatinina": 0.92,
        "nitrogeno_ureico": 31,
        "sodio": 139,
        "potasio": 4.5,
        "dreo": "No",
        "troponinas_alteradas": "No",
        "ecg_alterado": "No",
        "rnm_protocolo_stroke": "No",
        "dva": "No",
        "transfusiones": "No",
        "compromiso_conciencia": "No",
    }
    output = make_prediction(form_data)
    print(output)
