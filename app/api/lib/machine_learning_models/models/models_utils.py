import app.api.lib.machine_learning_models.prepare_data as prep
import app.api.lib.machine_learning_models.clean_data as c
from sklearn.metrics import classification_report, confusion_matrix
from typing import Callable
import joblib
import pandas as pd
from pathlib import Path


def file_exists_in_parent_folder(file_name: str) -> bool:
    current_folder = Path(__file__).resolve().parent
    path_file = current_folder / file_name
    return path_file.is_file()


def serialize_model(model, file_name: str, folder_model: str) -> None:
    """
    Serialize the trained model to a file.
    """
    base_path = prep.get_base_directory()
    file_path = f"{base_path}/models/{folder_model}/{file_name}"
    joblib.dump(model, file_path)


def create_dataset_model_predictions(
    file_name: str, model_folder: str, y_pred, y_test
) -> list:
    """
    Create a dataset with predictions from the model and save it to a CSV file.
    """
    df = pd.DataFrame({"y_true": y_test, "y_pred": y_pred})
    base_path = prep.get_base_directory()
    file_path = f"{base_path}/models/{model_folder}/metrics/{file_name}"
    c.save_df_to_csv(df, file_path, index=False)


def calculate_metrics_and_confussion_matrix(
    model_folder: str, metrics_file: str, training_function: Callable[[], None]
) -> bool:

    metrics_file_exists = file_exists_in_parent_folder(metrics_file)
    parent_folder = Path(__file__).resolve().parent
    file_path = parent_folder / model_folder / "metrics" / metrics_file
    if not metrics_file_exists:
        # rf_train.train_random_forest_model()
        training_function()

    df = pd.read_csv(file_path, sep=";", encoding="utf-8")
    y_true = df["y_true"]
    y_pred = df["y_pred"]

    report = classification_report(y_true, y_pred, output_dict=True)
    report_df = pd.DataFrame(report).transpose()
    report_path = parent_folder / model_folder / "metrics" / "classification_report.csv"
    report_df.to_csv(report_path, sep=";", encoding="utf-8")

    cm = confusion_matrix(y_true, y_pred)
    cm_df = pd.DataFrame(cm)
    cm_path = parent_folder / model_folder / "metrics" / "confusion_matrix.csv"
    cm_df.to_csv(cm_path, sep=";", encoding="utf-8", index=True)

    return (report_df, cm_df)


def get_means_numerical_columns(df: pd.DataFrame, columns: list[str]) -> dict:
    """
    Get means of numerical columns.
    """
    return {
        col: pd.to_numeric(df[col], errors="coerce").mean(skipna=True)
        for col in columns
    }


def get_mode_categorical_columns(df: pd.DataFrame, columns: list[str]) -> dict:
    """
    Get mode of categorical columns.
    """
    return {
        col: df[col].mode()[0] if not df[col].mode().empty else None for col in columns
    }


def get_mode_binary_columns(df: pd.DataFrame, columns: list[str]) -> dict:
    """
    Get mode of binary columns.
    """
    return {
        col: df[col].mode()[0] if not df[col].mode().empty else None for col in columns
    }


def get_random_value_from_column(df: pd.DataFrame, column: str) -> dict:
    """
    Get mode of categorical columns.
    """
    return df[column].sample(n=1).iloc[0]
