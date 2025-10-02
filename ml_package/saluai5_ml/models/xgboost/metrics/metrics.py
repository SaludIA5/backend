import app.api.lib.machine_learning_models.models.models_utils as u
import app.api.lib.machine_learning_models.models.xgboost.train as xg_train


def metrics_xgboost_model() -> bool:
    return u.calculate_metrics_and_confussion_matrix(
        "xgboost", "model_predictions.csv", xg_train.train_xgboost_model
    )


if __name__ == "__main__":
    metrics_xgboost_model()
