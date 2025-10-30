from pathlib import Path

import joblib
import pandas as pd
from saluai5_ml.preprocessing.cleaner import data_cleaner, save_df_to_csv
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, OneHotEncoder


def get_base_directory() -> Path:
    """Get the base directory of the package."""
    return Path(__file__).resolve().parent.parent


def preprocess_data(file_name: str) -> pd.DataFrame:
    pass


def serialize_encoder(encoder, file_name: str) -> None:
    """
    Serialize the encoder to a file.
    """
    base_path = get_base_directory()
    file_path = base_path / "encoders" / file_name
    joblib.dump(encoder, file_path)


def read_csv_file(file_name: str) -> pd.DataFrame:
    """
    Read a CSV file and return a DataFrame.
    """
    base_directory = get_base_directory()
    file_path = base_directory / "data" / "processed" / file_name
    return pd.read_csv(file_path, sep=";", encoding="utf-8")


def transform_target_column(df: pd.DataFrame, target_column: str) -> pd.DataFrame:
    """
    Transform the target column to binary values.
    """
    df_copy = df.copy()
    if target_column in df_copy.columns:
        df_copy[target_column] = df_copy[target_column].apply(
            lambda x: 1 if x == "PERTINENTE" else 0
        )
    return df_copy


def apply_label_encoding(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Apply Label Encoding to a specified column.
    """
    label_encoder = LabelEncoder()
    df[column + "_encoded"] = label_encoder.fit_transform(df[column])
    serialize_encoder(label_encoder, f"{column}_label_encoder.pkl")
    # df_test[column + "_encoded"] = label_encoder.transform(df_test[column])
    # return df_train, df_test
    return df


def transform_categorical_columns(
    df_train: pd.DataFrame, df_test: pd.DataFrame, categorical_columns: list[str]
) -> pd.DataFrame:
    """
    Transform categorical columns using One-Hot Encoding.
    """
    encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")

    df_train_encoded = encoder.fit_transform(df_train[categorical_columns])
    df_test_encoded = encoder.transform(df_test[categorical_columns])
    serialize_encoder(encoder, "categorical_one_hot_encoder.pkl")

    x_train_ohe = pd.DataFrame(
        df_train_encoded,
        columns=encoder.get_feature_names_out(categorical_columns),
        index=df_train.index,
    )
    x_test_ohe = pd.DataFrame(
        df_test_encoded,
        columns=encoder.get_feature_names_out(categorical_columns),
        index=df_test.index,
    )

    x_train = pd.concat(
        [df_train.drop(columns=categorical_columns), x_train_ohe], axis=1
    )
    x_test = pd.concat([df_test.drop(columns=categorical_columns), x_test_ohe], axis=1)
    return x_train, x_test


def apply_scaling(
    df_train: pd.DataFrame, df_test: pd.DataFrame, columns_to_scale: list[str]
) -> pd.DataFrame:
    """
    Apply Min-Max Scaling to numerical columns.
    """
    scaler = MinMaxScaler()
    df_train[columns_to_scale] = scaler.fit_transform(df_train[columns_to_scale])
    df_test[columns_to_scale] = scaler.transform(df_test[columns_to_scale])
    serialize_encoder(scaler, "numerical_min_max_scaler.pkl")
    return df_train, df_test


def create_train_test_datasets(df: pd.DataFrame, target_column: str, test_size: float):
    """
    Create training and testing datasets.
    """
    feature_columns = [col for col in df.columns if col != target_column]
    x = df[feature_columns]
    y = df[target_column]
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=test_size, random_state=42, stratify=y
    )
    return x_train, x_test, y_train, y_test


def save_preprocessed_dataset(datasets: list, file_name: str) -> None:
    """
    Save the preprocessed training dataset to a CSV file.
    """
    x_train, x_test, y_train, y_test = datasets
    df_train = x_train.copy()
    df_train["split_train"] = 1
    df_train["target"] = y_train.values

    df_test = x_test.copy()
    df_test["split_train"] = 0
    df_test["target"] = y_test.values

    df_combined = pd.concat([df_train, df_test], axis=0).reset_index(drop=True)

    base_directory = get_base_directory()
    file_path = f"{base_directory}/datasets/{file_name}"
    save_df_to_csv(df_combined, file_path)


def preprocessing_initial_data(file_name: str, file_name_clean: str) -> pd.DataFrame:
    data_cleaner(file_name, file_name_clean)
    df = read_csv_file(file_name_clean)

    target_columnn = "validacion"
    df = transform_target_column(df, target_columnn)

    # df = apply_label_encoding(df, "diagnostics")

    x_train, x_test, y_train, y_test = create_train_test_datasets(
        df, target_columnn, test_size=0.2
    )

    # categorical_columns = ["tipo", "tipo_alerta_ugcc", "tipo_cama", "triage", "diagnostics_encoded"]
    categorical_columns = ["tipo", "tipo_alerta_ugcc", "tipo_cama", "triage"]
    x_train, x_test = transform_categorical_columns(
        x_train, x_test, categorical_columns
    )

    numerical_columns = [
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
    x_train, x_test = apply_scaling(x_train, x_test, numerical_columns)

    datasets_train_test = [x_train, x_test, y_train, y_test]

    invalid_columns_to_train = [
        "diagnostics",
        "numero_episodio",
        target_columnn,
    ] + categorical_columns
    valid_columns_to_train = [
        col for col in x_train.columns if col not in invalid_columns_to_train
    ]

    save_preprocessed_dataset(datasets_train_test, "preproc_data.csv")
    return (datasets_train_test, valid_columns_to_train, target_columnn)


if __name__ == "__main__":
    preprocessing_initial_data("initial_data.xlsx", "initial_data_cleaned.csv")
