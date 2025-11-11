import pandas as pd
import numpy as np

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
    
    """
    Se encarga del preprocesamiento de datos antes del entrenamiento o predicción.
    - Limpieza de valores nulos
    - Conversión de tipos
    - Normalización y codificación
    """
        
    def upload_data(self, df: pd.DataFrame) -> None:
        self.data = df
        self.data_columns = self.data.columns

    def impute_binary_columns(self) -> None:
        """
        Imputa valores faltantes en columnas binarias usando la moda de cada columna.
        Modifica self.data in-place (no retorna nada).
        """
        for col in self.binary_columns:
            if col in self.data_columns:
                self.data[col] = self.data[col].replace("", np.nan)
                mode_value = self.data[col].mode(dropna=True)
                mode_value = mode_value[0] if not mode_value.empty else False
                self.data[col] = self.data[col].fillna(mode_value)


    def impute_numerical_columns(self) -> None:
        """
        Imputa valores faltantes en columnas numéricas usando el promedio (mean) 
        de cada columna. Modifica self.data in-place (no retorna nada).
        """
        for col in self.numerical_columns:
            if col in self.data_columns:
                self.data[col] = self.data[col].replace("", np.nan)
                mean_value = self.data[col].mean(skipna=True)
                if pd.isna(mean_value):
                    mean_value = 0.0

                self.data[col] = self.data[col].fillna(mean_value)

    def impute_categorical_columns(self) -> None:
        """
        Imputa valores faltantes en columnas categóricas usando la moda 
        (valor más frecuente) de cada columna.
        Modifica self.data in-place (no retorna nada).
        """
        for col in self.categorical_columns:
            if col in self.data_columns:
                self.data[col] = self.data[col].replace("", np.nan)
                mode_value = self.data[col].mode(dropna=True)
                mode_value = mode_value[0] if not mode_value.empty else None
                self.data[col] = self.data[col].fillna(mode_value)
    
    def impute_multicategorical_columns(self) -> None:
        """
        Imputa valores faltantes en columnas multicategóricas usando [].
        Modifica self.data in-place (no retorna nada).
        """
        for col in self.multicategorical_columns:
            if col in self.data_columns:
                self.data[col] = self.data[col].apply(lambda x: x if isinstance(x, list) and not pd.isna(x) else [])
    
    def impute_data(self) -> None:
        """
        Imputa valores faltantes en todas las columnas del dataset,
        incluyendo binarias, numéricas y categóricas.
        Modifica self.data in-place (no retorna nada).
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
            if col in self.data_columns:
                self.data[col] = self.data[col].apply(self.map_binary_value)

    def map_binary_value(self, value):
        """
        Mapea valores binarios.
        """
        if value is None or (isinstance(value, float) and np.isnan(value)) or pd.isna(value):
            return 0
        if isinstance(value, str):
            if value in ["SI", "Si", "Sí", "si", "sí", "True"]:
                return 1
            elif value in ["NO", "No", "no", "False", "None"]:
                return 0
        elif isinstance(value, bool):
            return 1 if value else 0
        
        return 0
    
    def run_preprocessing(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ejecuta el preprocesamiento completo de datos.
        Retorna el DataFrame preprocesado.
        """
        self.upload_data(df)
        self.impute_data()
        self.transform_binary_columns()
        return self.data