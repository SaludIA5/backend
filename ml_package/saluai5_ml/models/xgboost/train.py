import saluai5_ml.models.utils as u
import saluai5_ml.preprocessing.transformer as prep
from xgboost import XGBClassifier


def train_xgboost_model() -> None:

    datasets, features, _ = prep.preprocessing_initial_data(
        "initial_data.xlsx", "initial_data_cleaned.csv"
    )
    x_train, x_test, y_train, y_test = datasets
    xgboost_model = XGBClassifier(
        objective="binary:logistic",
        learning_rate=0.05,
        n_estimators=300,
        max_depth=4,
        min_child_weight=3,
        gamma=0.5,
        subsample=0.7,
        colsample_bytree=0.4,
        reg_alpha=0.5,
        reg_lambda=1.0,
        random_state=42,
        use_label_encoder=False,
        eval_metric="logloss",
    )
    xgboost_model.fit(x_train[features], y_train)
    u.serialize_model(xgboost_model, "xgboost_model.pkl", "xgboost")
    y_pred = xgboost_model.predict(x_test[features])
    u.create_dataset_model_predictions(
        "model_predictions.csv", "xgboost", y_pred, y_test
    )
