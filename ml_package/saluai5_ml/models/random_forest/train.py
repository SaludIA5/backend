import saluai5_ml.models.utils as u
import saluai5_ml.preprocessing.transformer as prep
from sklearn.ensemble import RandomForestClassifier


def train_random_forest_model() -> None:
    datasets, features, _ = prep.preprocessing_initial_data(
        "initial_data.xlsx", "initial_data_cleaned.csv"
    )
    x_train, x_test, y_train, y_test = datasets

    rf_model = RandomForestClassifier(
        n_estimators=100, max_depth=10, bootstrap=True, random_state=42
    )
    rf_model.fit(x_train[features], y_train)
    u.serialize_model(rf_model, "random_forest_model.pkl", "random_forest")
    y_pred = rf_model.predict(x_test[features])
    u.create_dataset_model_predictions(
        "model_predictions.csv", "random_forest", y_pred, y_test
    )


if __name__ == "__main__":
    train_random_forest_model()
