"""Train a Random Forest classifier using the included synthetic demo dataset.
Run: python -m ml.train_model
Replace the synthetic CSV with real Jenkins history before production use.
"""
from pathlib import Path
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

ROOT = Path(__file__).resolve().parent.parent
df = pd.read_csv(ROOT / "data" / "pipeline_history.csv")
features = ["changed_files","test_failures","previous_failures","build_duration","cpu_usage","coverage"]
X, y = df[features], df["failed"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2, random_state=42, stratify=y)
model = RandomForestClassifier(n_estimators=180, max_depth=7, class_weight="balanced", random_state=42)
model.fit(X_train, y_train)
print("Accuracy:", round(accuracy_score(y_test, model.predict(X_test)), 3))
print(classification_report(y_test, model.predict(X_test)))
joblib.dump(model, ROOT / "ml" / "risk_model.joblib")
print("Saved ml/risk_model.joblib")
