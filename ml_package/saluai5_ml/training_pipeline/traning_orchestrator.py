from typing import List
import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.databases.postgresql.models import Episode

class TrainingOrchestrator:
    def __init__(self, data_path="data/train_data.csv", model_dir="models/"):
        self.data_path = data_path
        self.model_dir = model_dir
        self.model = None
        os.makedirs(model_dir, exist_ok=True)

    # 1️⃣ Data fetch
    def data_fetcher(self):
        print("📥 Fetching data...")
        df = pd.read_csv(self.data_path)
        return df

    # 2️⃣ Data clean
    def data_cleaner(self, df):
        print("🧹 Cleaning data...")
        df = df.dropna()
        return df

    # 3️⃣ Model training
    def model_training(self, df):
        print("🤖 Training model...")
        X = df.drop("target", axis=1)
        y = df["target"]
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        self.model = model
        return model

    # 4️⃣ Evaluation (opcional)
    def evaluate(self, df):
        print("📊 Evaluating model...")
        X = df.drop("target", axis=1)
        y = df["target"]
        acc = self.model.score(X, y)
        print(f"✅ Accuracy: {acc:.4f}")
        return acc

    # 5️⃣ Save and version
    def save_and_version(self, acc):
        print("💾 Saving model...")
        registry_path = os.path.join(self.model_dir, "registry.json")
        if os.path.exists(registry_path):
            with open(registry_path, "r") as f:
                registry = json.load(f)
        else:
            registry = {"versions": []}

        new_version = len(registry["versions"]) + 1
        model_path = f"{self.model_dir}/model_v{new_version}.pkl"

        joblib.dump(self.model, model_path)
        joblib.dump(self.model, f"{self.model_dir}/current_model.pkl")

        registry["versions"].append({
            "version": new_version,
            "accuracy": acc,
            "path": model_path,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        with open(registry_path, "w") as f:
            json.dump(registry, f, indent=4)

        print(f"📦 Model v{new_version} saved ({acc:.4f})")

    # 6️⃣ Pipeline end-to-end
    def run(self):
        df = self.data_fetcher()
        df = self.data_cleaner(df)
        self.model_training(df)
        acc = self.evaluate(df)
        self.save_and_version(acc)
        print("🏁 Training pipeline completed!")