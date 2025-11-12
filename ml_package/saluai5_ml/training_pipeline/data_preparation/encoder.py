import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer, MinMaxScaler, OneHotEncoder
from typing import List
import joblib
from pathlib import Path

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
        
    def upload_data(self, data: List[pd.DataFrame], version: str) -> None:
        self.features_train = data[0]
        self.features_test = data[1]
        self.label_version = version
        
    def get_base_directory_package(self) -> Path:
        """
        Obtiene el directorio base del proyecto.
        """
        return Path(__file__).resolve().parent.parent.parent
    
    def get_versioning_label(self, category: str) -> None:
        """
		Crea una etiqueta de versión para los encoders.
		"""
        return f"{category}/{self.label_version}.pkl"
    
    def serialize_encoder(self, encoder, category: str) -> None:
        """
		Serializa el encoder en un archivo.
		"""
        file_name = self.get_versioning_label(category)
        base_path = self.get_base_directory_package()
        file_path = base_path / "encoders_repository" / file_name
        joblib.dump(encoder, file_path)

    def encode_categorical_columns(self) -> None:
        """
		Codifica columnas categóricas usando One-Hot Encoding.
		"""
        existing_cols = [c for c in self.categorical_columns if c in self.features_train.columns]
        print(f"Columnas categóricas a codificar: {existing_cols}")
        if not existing_cols:
            print("⚠️ No se encontraron columnas categóricas para codificar.")
            return
        
        print("Tipos de las columnas categóricas:")
        print(self.features_train[self.categorical_columns].dtypes)

        print("\nCantidad de valores únicos:")
        for col in self.categorical_columns:
            print(col, "→", self.features_train[col].nunique(), "valores únicos")
            print(self.features_train[col].unique()[:10])
        categorical_encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
        features_train_encoded = categorical_encoder.fit_transform(self.features_train[self.categorical_columns])
        features_test_encoded = categorical_encoder.transform(self.features_test[self.categorical_columns])
        self.serialize_encoder(categorical_encoder, "categorical")
        features_train_ohe = pd.DataFrame(
			features_train_encoded,
			columns=categorical_encoder.get_feature_names_out(self.categorical_columns),
			index=self.features_train.index,
		)
        features_test_ohe = pd.DataFrame(
			features_test_encoded,
			columns=categorical_encoder.get_feature_names_out(self.categorical_columns),
			index=self.features_test.index,
		)
        self.features_train = pd.concat(
			[self.features_train.drop(columns=self.categorical_columns), features_train_ohe], axis=1
		)
        self.features_test = pd.concat([self.features_test.drop(columns=self.categorical_columns), features_test_ohe], axis=1)
        
    def encode_multicategorical_columns(self) -> None:
        """
		Codifica columnas multicategóricas usando Multi Label Encoder.
		"""
        multicategorical_column = self.multicategorical_columns[0]
        mlb_encoder = MultiLabelBinarizer()
        encoded_train = mlb_encoder.fit_transform(self.features_train[multicategorical_column])
        encoded_test = mlb_encoder.transform(self.features_test[multicategorical_column])
        encoded_col_names = [f"{multicategorical_column}_{cls}" for cls in mlb_encoder.classes_]
        train_df = pd.DataFrame(encoded_train, columns=encoded_col_names, index=self.features_train.index)
        test_df = pd.DataFrame(encoded_test, columns=encoded_col_names, index=self.features_test.index)
        self.features_train = pd.concat([self.features_train.drop(columns=[multicategorical_column]), train_df], axis=1)
        self.features_test = pd.concat([self.features_test.drop(columns=[multicategorical_column]), test_df], axis=1)
        self.serialize_encoder(mlb_encoder, "multilabel")
        
    def normalize_numerical_columns(self) -> None:
        """
		Aplica min max scaler a las columnas numericas.
		"""
        scaler = MinMaxScaler()
        self.features_train[self.numerical_columns] = scaler.fit_transform(self.features_train[self.numerical_columns])
        self.features_test[self.numerical_columns] = scaler.transform(self.features_test[self.numerical_columns])
        self.serialize_encoder(scaler, "numerical")
    
    def encode(self, data: List[pd.DataFrame], version: str) -> pd.DataFrame:
        """
        Ejecuta el preprocesamiento completo de datos.
        Retorna el DataFrame preprocesado.
        """
        self.upload_data(data, version)
        self.encode_categorical_columns()
        self.normalize_numerical_columns()
        self.encode_multicategorical_columns()
        self.print_successful_operation()
        return self.features_train, self.features_test
    
    def print_successful_operation(self) -> None:
        """Imprime mensaje de exito"""
        print(f"✅ Datos codificados: {len(self.features_train)} filas de entrenamiento y {len(self.features_test)} filas de testing")

if __name__ == "__main__":
    encoder = DataEncoder()
    print(encoder)