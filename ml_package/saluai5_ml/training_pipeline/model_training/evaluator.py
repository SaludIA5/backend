# import pandas as pd
# from typing import List
# from sklearn.metrics import f1_score

# class ModelEvaluator:
    
#     """
#     Calcula las métricas de evaluación para un modelo de machine learning clásico.
#     """
#     def __init__(self):
#         self.metric = "f1_score"
        
#     def upload_data(self, data: List[pd.DataFrame], model) -> None:
#         """
# 		Carga los datos de entrenamiento y la versión del modelo.
#         """
#         self.features_train = data[0]
#         self.target_train = data[1]
#         self.target_test = data[2]
#         self.model = model
    
# 	def calculate_metrics(self, y_true, y_pred) -> float:
# 		"""Calcula la métrica F1-Score."""
# 		from sklearn.metrics import f1_score
# 		f1 = f1_score(y_true, y_pred, average='weighted')
# 		return f1		
#     def evaluate_model(self, data: List[pd.DataFrame], model) -> None:
#         """Entrena el modelo de machine learning clásico."""
#         model = self.models_factory()
#         model.fit(self.features_train, self.target_train)
#         self.model_serializer(model, self.model_name)
#         self.print_successful_operation()
#         return model
        
        
#     def print_successful_operation(self, metrics) -> None:
#         """Imprime mensaje de exito"""
#         print(f"✅ Modelo evaluado con métrica F1-Score: {round(metrics, 2) * 100}%")