import pandas as pd


class DataEncoder:

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

    """
    Se encarga de codificar variables categóricas, multicategóricas y
    normalizar los datos.
    """

    def upload_data(self, data: pd.DataFrame, encoders: any, model: any) -> None:
        self.data = data
        self.model = model
        self.categorical_encoder = encoders[0]
        self.multilabel_encoder = encoders[1]
        self.numerical_encoder = encoders[2]

    def encode_categorical_columns(self) -> None:
        """
        Codifica columnas categóricas usando One-Hot Encoding.
        """

        data_encoded = self.categorical_encoder.transform(
            self.data[self.categorical_columns]
        )

        data_ohe = pd.DataFrame(
            data_encoded,
            columns=self.categorical_encoder.get_feature_names_out(
                self.categorical_columns
            ),
            index=self.data.index,
        )

        self.data = pd.concat(
            [
                self.data.drop(columns=self.categorical_columns),
                data_ohe,
            ],
            axis=1,
        )

    def encode_multicategorical_columns(self) -> None:
        """
        Codifica columnas multicategóricas usando Multi Label Encoder.
        """
        multicategorical_column = self.multicategorical_columns[0]

        encoded_data = self.multilabel_encoder.transform(
            self.data[multicategorical_column]
        )
        encoded_col_names = [
            f"{multicategorical_column}_{cls}"
            for cls in self.multilabel_encoder.classes_
        ]

        data_df = pd.DataFrame(
            encoded_data, columns=encoded_col_names, index=self.data.index
        )
        self.data = pd.concat(
            [self.data.drop(columns=[multicategorical_column]), data_df],
            axis=1,
        )

    def normalize_numerical_columns(self) -> None:
        """
        Aplica min max scaler a las columnas numericas.
        """
        self.data[self.numerical_columns] = self.numerical_encoder.transform(
            self.data[self.numerical_columns]
        )

    def align_features(self):
        expected_cols = list(self.model.feature_names_in_)
        return self.data[expected_cols]

    def encode(self, data: pd.DataFrame, artifacts: any) -> pd.DataFrame:
        """
        Codifica y normaliza los datos.
        """
        self.upload_data(data, artifacts["data_encoders"], artifacts["model"])
        self.encode_categorical_columns()
        self.normalize_numerical_columns()
        self.encode_multicategorical_columns()
        self.print_successful_operation()
        data_encoded = self.align_features()
        return data_encoded

    def print_successful_operation(self) -> None:
        """Imprime mensaje de exito"""
        print("✅ Datos codificados")
