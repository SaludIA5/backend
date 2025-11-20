import numpy as np
import pandas as pd


class DataCleaner:

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
    exclude_columns = ["id_episodio", "validacion"]
    null_like_strings = ["", " ", "\t", "nan", "NaN", "NULL", "null", "None", "none"]

    """
    Se encarga del preprocesamiento de datos antes del entrenamiento o predicción.
    - Limpieza de valores nulos
    - Conversión de tipos
    - Normalización y codificación
    """

    def upload_data(
        self, df_db: pd.DataFrame, df_request: pd.DataFrame, labels
    ) -> None:
        self.data_db = df_db
        self.data_db_columns = self.data_db.columns
        self.data_request = pd.DataFrame([df_request])
        self.labels = labels

    def filter_episode_columns(self) -> None:
        """
        Filtra las columnas del DataFrame de la base de datos para que solo
        queden las relevantes para el modelo.
        Modifica self.data_db in-place (no retorna nada).
        """
        relevant_columns = (
            self.numerical_columns
            + self.binary_columns
            + self.categorical_columns
            + self.multicategorical_columns
        )
        self.data_request = self.data_request[relevant_columns].copy()

    def impute_binary_columns(self) -> None:
        """
        Imputa valores faltantes en columnas binarias usando la moda de cada columna.
        Modifica self.data_db in-place (no retorna nada). Rellena el df de la request
        """
        for col in self.binary_columns:
            if col in self.data_db_columns:
                self.data_db[col] = self.data_db[col].replace("", np.nan)
                mode_value = self.data_db[col].mode(dropna=True)
                mode_value = mode_value[0] if not mode_value.empty else False

                if col in self.data_request.columns:
                    self.data_request[col] = self.data_request[col].replace(
                        self.null_like_strings, np.nan
                    )
                    self.data_request[col] = (
                        self.data_request[col]
                        .fillna(mode_value)
                        .infer_objects(copy=False)
                    )

    def impute_numerical_columns(self) -> None:
        """
        Imputa valores faltantes en columnas numéricas usando el promedio (mean)
        de cada columna. Modifica self.data_db in-place (no retorna nada).
        """
        for col in self.numerical_columns:
            if col in self.data_db_columns:
                self.data_db[col] = self.data_db[col].replace("", np.nan)
                mean_value = self.data_db[col].mean(skipna=True)
                if pd.isna(mean_value):
                    mean_value = 0.0

                if col in self.data_request.columns:
                    self.data_request[col] = self.data_request[col].replace(
                        self.null_like_strings, np.nan
                    )
                    self.data_request[col] = (
                        self.data_request[col]
                        .fillna(mean_value)
                        .infer_objects(copy=False)
                    )

    def impute_categorical_columns(self) -> None:
        """
        Imputa valores faltantes en columnas categóricas usando la moda
        (valor más frecuente) de cada columna.
        Modifica self.data_db in-place (no retorna nada).
        """
        for col in self.categorical_columns:
            if col in self.data_db_columns:
                self.data_db[col] = self.data_db[col].replace("", np.nan)
                mode_value = self.data_db[col].mode(dropna=True)
                mode_value = mode_value[0] if not mode_value.empty else None

                if col in self.data_request.columns:
                    self.data_request[col] = self.data_request[col].replace(
                        self.null_like_strings, np.nan
                    )
                    self.data_request[col] = (
                        self.data_request[col]
                        .fillna(mode_value)
                        .infer_objects(copy=False)
                    )
                    if col in ["tipo", "tipo_alerta_ugcc"]:
                        self.data_request[col] = (
                            self.data_request[col].astype("string").str.upper()
                        )

    def impute_multicategorical_columns(self) -> None:
        """
        Imputa valores faltantes en columnas multicategóricas usando [].
        Modifica self.data_db in-place (no retorna nada).
        """
        for col in self.multicategorical_columns:
            if col in self.data_request.columns:
                self.data_request[col] = self.data_request[col].apply(
                    self.clean_multilabels
                )

    def clean_multilabels(self, labels):
        """
        Limpia los labels multicategoricos para que solo contengan valores validos.
        """
        if not isinstance(labels, list):
            return []
        cleaned = []
        for x in labels:
            if x is None or (isinstance(x, float) and np.isnan(x)):
                continue
            if not isinstance(x, str):
                continue
            if x in self.labels:
                cleaned.append(x)
        return cleaned

    def impute_data(self) -> None:
        """
        Imputa valores faltantes en todas las columnas del dataset,
        incluyendo binarias, numéricas y categóricas.
        Modifica self.data_db in-place (no retorna nada).
        """
        self.impute_binary_columns()
        self.impute_numerical_columns()
        self.impute_categorical_columns()
        self.impute_multicategorical_columns()

    def transform_binary_columns(self) -> None:
        """
        Codifica columnas binarias a numérico (0/1).
        """
        for col in self.binary_columns:
            if col in self.data_db_columns:
                self.data_request[col] = self.data_request[col].apply(
                    self.map_binary_value
                )

    def transform_triage_column(self) -> None:
        """
        Convierte la columna 'triage' a string."""
        self.data_request["triage"] = self.data_request["triage"].apply(
            lambda x: (
                ""
                if pd.isna(x)
                else str(int(x)) if isinstance(x, (float, int)) else str(x)
            )
        )

    def map_binary_value(self, value):
        """
        Mapea valores binarios.
        """
        if (
            value is None
            or (isinstance(value, float) and np.isnan(value))
            or pd.isna(value)
        ):
            return 0
        if isinstance(value, str):
            if value in ["SI", "Si", "Sí", "si", "sí", "True"]:
                return 1
            elif value in ["NO", "No", "no", "False", "None"]:
                return 0
        elif isinstance(value, bool):
            return 1 if value else 0

        return 0

    def run_preprocessing(self, data, label_classes) -> pd.DataFrame:
        """
        Ejecuta el preprocesamiento completo de datos.
        Retorna el DataFrame preprocesado.
        """
        self.upload_data(data[0], data[1], label_classes)
        self.filter_episode_columns()
        self.impute_data()
        self.transform_triage_column()
        self.transform_binary_columns()
        self.print_successful_operation()
        return self.data_request

    def print_successful_operation(self) -> None:
        """Imprime mensaje de exito"""
        print("✅ Datos preprocesados")
