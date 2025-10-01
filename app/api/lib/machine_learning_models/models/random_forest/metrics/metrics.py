import app.api.lib.machine_learning_models.models.models_utils as u
import app.api.lib.machine_learning_models.models.random_forest.train as rf_train


def metrics_random_forest_model() -> bool:
    return u.calculate_metrics_and_confussion_matrix(
        "random_forest", "model_predictions.csv", rf_train.train_random_forest_model
    )


if __name__ == "__main__":
    metrics_random_forest_model()
