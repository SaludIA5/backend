import pandas as pd
from sklearn.model_selection import train_test_split


class DataSplitter:

    binary_columns = [
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
    categorical_columns = ["tipo", "tipo_alerta_ugcc", "tipo_cama", "triage"]
    multicategorical_columns = ["diagnostics"]
    target_column = ["validacion"]
    exclude_columns = ["id_episodio"]

    """
    Se encarga de hacer el train/test split de los datos.
    """

    def __init__(self, train_size: float = 0.8):
        self.train_size = train_size

    def upload_data(self, df: pd.DataFrame) -> None:
        """
        Carga el dataframe a procesar.
        """
        self.data = df

    def build_train_test_data(self, df: pd.DataFrame) -> tuple[pd.DataFrame]:
        """
        Crea los copnjuntos de entrenamiento y testing para el modelo.
        """
        self.upload_data(df)
        features_columns = (
            self.numerical_columns
            + self.categorical_columns
            + self.binary_columns
            + self.multicategorical_columns
        )
        x = self.data[features_columns]
        y = (
            self.data[self.target_column]
            if isinstance(self.target_column, str)
            else self.data[self.target_column[0]]
        )
        x_train, x_test, y_train, y_test = train_test_split(
            x, y, test_size=1 - self.train_size, random_state=23, stratify=y
        )
        self.print_successful_operation(x_train, x_test)
        return x_train, x_test, y_train, y_test

    def print_successful_operation(self, x_train, x_test) -> None:
        """Imprime mensaje de exito"""
        print(
            f"✅ Conjuntos de train/test creados: {len(x_train)} filas de entrenamiento y {len(x_test)} filas de testing"
        )
