# SALUAI5 ML Package

Paquete de Machine Learning para la predicción de pertinencia de episodios médicos.

## 📦 Estructura del Paquete

```
saluai5_ml/
├── __init__.py              # Exports principales (predict_rf, predict_xgb)
│
├── data/
│   ├── raw/                 # Datos crudos (Excel)
│   │   └── initial_data.xlsx
│   └── processed/           # Datos procesados (CSV)
│       ├── initial_data_cleaned.csv
│       └── preproc_data.csv
│
├── preprocessing/
│   ├── cleaner.py           # Limpieza de datos
│   └── transformer.py       # Transformaciones y encoding
│
├── models/
│   ├── utils.py             # Utilidades compartidas
│   ├── random_forest/
│   │   ├── inference.py     # Predicción con Random Forest
│   │   ├── train.py         # Entrenamiento Random Forest
│   │   ├── random_forest_model.pkl
│   │   └── metrics/
│   │       ├── metrics.py
│   │       ├── classification_report.csv
│   │       ├── confusion_matrix.csv
│   │       └── model_predictions.csv
│   └── xgboost/
│       ├── inference.py     # Predicción con XGBoost
│       ├── train.py         # Entrenamiento XGBoost
│       ├── xgboost_model.pkl
│       └── metrics/
│           └── (similar a RF)
│
└── encoders/
    ├── categorical_one_hot_encoder.pkl
    └── numerical_min_max_scaler.pkl
```

## 🚀 Instalación

El paquete está diseñado para instalarse en modo editable:

```bash
# Desde el directorio raíz del backend
pip install -e ./ml_package

# O con Poetry (recomendado)
poetry add ./ml_package --editable
```

## 💻 Uso

### Predicción Simple

```python
from saluai5_ml import predict_rf, predict_xgb

# Datos del episodio
episode_data = {
    "tipo": "SIN ALERTA",
    "tipo_alerta_ugcc": "SIN ALERTA",
    "triage": 3,
    "presion_sistolica": 160,
    "presion_diastolica": 95,
    "temperatura_c": 36.5,
    # ... más campos
}

# Predicción con Random Forest
result = predict_rf(episode_data)
# {'prediction': 1, 'probability': 0.87, 'label': 'PERTINENTE', 'model': 'random_forest'}

# Predicción con XGBoost
result = predict_xgb(episode_data)
```

## 🏋️ Entrenamiento de Modelos

### Entrenar Random Forest

```bash
# Desde el directorio raíz del backend
poetry run python -m saluai5_ml.models.random_forest.train
```

El script:
1. Carga y preprocesa datos
2. Entrena el modelo Random Forest
3. Guarda el modelo en `models/random_forest/random_forest_model.pkl`
4. Genera métricas en `models/random_forest/metrics/`

### Entrenar XGBoost

```bash
poetry run python -m saluai5_ml.models.xgboost.train
```

### Preprocesamiento de Datos

```bash
# Limpiar datos desde Excel
poetry run python -m saluai5_ml.preprocessing.cleaner

# Transformar y preparar datos
poetry run python -m saluai5_ml.preprocessing.transformer
```

## 📊 Características del Modelo

### Variables de Entrada

**Binarias (21):**
- Antecedentes médicos (cardiaco, diabetes, hipertensión)
- Procedimientos (cirugía, hemodinamia, endoscopia, diálisis, etc.)
- Indicadores (DREO, troponinas, ECG, RNM, DVA, etc.)

**Numéricas (15):**
- Signos vitales (presión, temperatura, saturación, frecuencias)
- Scores (Glasgow)
- Soporte respiratorio (FiO2)
- Laboratorios (PCR, hemoglobina, creatinina, BUN, electrolitos)

**Categóricas (4):**
- Tipo de episodio
- Tipo de alerta UGCC
- Tipo de cama
- Triage

### Variables de Salida

- **Predicción:** 0 (NO PERTINENTE) o 1 (PERTINENTE)
- **Probabilidad:** 0.0 - 1.0 (confianza del modelo)
- **Label:** "NO PERTINENTE" o "PERTINENTE"
- **Model:** "random_forest" o "xgboost"

## 🔧 Pipeline de Procesamiento

1. **Limpieza** (`cleaner.py`):
   - Carga Excel con datos crudos
   - Filtra episodios válidos
   - Elimina columnas irrelevantes
   - Renombra columnas
   - Codifica variables binarias (Sí/No → 1/0)

2. **Transformación** (`transformer.py`):
   - Aplica Label Encoding
   - OneHot Encoding para categóricas
   - MinMax Scaling para numéricas
   - Split train/test
   - Serializa encoders

3. **Entrenamiento** (`train.py`):
   - Carga datos preprocesados
   - Entrena modelo
   - Genera métricas
   - Serializa modelo

4. **Inferencia** (`inference.py`):
   - Preprocesa datos de entrada
   - Rellena valores faltantes
   - Aplica encoders
   - Ejecuta predicción

## 📈 Métricas de Evaluación

Cada modelo genera:

- **Classification Report:** Precision, Recall, F1-Score por clase
- **Confusion Matrix:** Matriz de confusión
- **Model Predictions:** Predicciones vs valores reales

Ubicación: `models/{model_name}/metrics/`

## 🧪 Testing

```bash
# Verificar que el paquete funciona
poetry run python -c "from saluai5_ml import predict_rf; print('✅ OK')"

# Tests de integración
poetry run pytest tests/test_predictions.py
```

## 📦 Dependencias

- `pandas>=2.0.0,<3.0.0`
- `numpy>=1.24.0,<2.0.0`
- `scikit-learn>=1.3.0,<2.0.0`
- `xgboost>=2.0.0,<4.0.0`
- `joblib>=1.3.0,<2.0.0`
- `openpyxl>=3.1.0,<4.0.0`


## 🤝 Integración con Backend

El backend de FastAPI importa este paquete:

```python
# app/services/prediction_service.py
from saluai5_ml import predict_rf, predict_xgb

class PredictionService:
    @staticmethod
    def predict_episode_pertinence(episode_data: dict, model_type: str):
        if model_type == "random_forest":
            return predict_rf(episode_data)
        else:
            return predict_xgb(episode_data)
```

## 📝 Notas Importantes

1. **Valores Faltantes:** El sistema rellena automáticamente con medias (numéricas) y modas (categóricas)

2. **Encoders:** Deben estar pre-entrenados en `encoders/`. Si no existen, ejecutar preprocessing

3. **Modelos:** Los `.pkl` deben existir. Si no, ejecutar entrenamiento

4. **Datos:** `initial_data.xlsx` debe estar en `data/raw/`

## 🐛 Troubleshooting

### "File not found" al cargar modelo
```bash
# Verificar que los modelos existen
ls ml_package/saluai5_ml/models/*/*.pkl
```

### "Encoder not found"
```bash
# Re-generar encoders
poetry run python -m saluai5_ml.preprocessing.transformer
```

### Errores de importación
```bash
# Reinstalar paquete
pip install -e ./ml_package --force-reinstall
```
