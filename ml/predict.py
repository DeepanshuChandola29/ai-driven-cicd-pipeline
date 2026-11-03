# Explainable demo risk model. If a trained model exists, use it; otherwise use
# a transparent weighted score so the project runs immediately without training.
from pathlib import Path
import joblib

MODEL_PATH = Path(__file__).resolve().parent / "risk_model.joblib"

def predict_risk(metrics):
    reasons = []
    score = 0
    if metrics["test_failures"] > 0:
        score += min(45, metrics["test_failures"] * 15)
        reasons.append(f'{metrics["test_failures"]} automated test failure(s) detected.')
    if metrics["previous_failures"] > 1:
        score += min(20, (metrics["previous_failures"] - 1) * 7)
        reasons.append("Recent pipeline history contains repeated failures.")
    if metrics["cpu_usage"] > 75:
        score += min(15, (metrics["cpu_usage"] - 75) * 0.8)
        reasons.append("High CPU utilization may affect runtime stability.")
    if metrics["coverage"] < 70:
        score += min(15, (70 - metrics["coverage"]) * 0.8)
        reasons.append("Test coverage is below the recommended 70% threshold.")
    if metrics["changed_files"] > 20:
        score += min(10, (metrics["changed_files"] - 20) * 0.5)
        reasons.append("Large change size increases release complexity.")
    if metrics["build_duration"] > 180:
        score += 8
        reasons.append("Build duration is unusually high.")
    try:
        if MODEL_PATH.exists():
            model = joblib.load(MODEL_PATH)
            features = [[metrics[k] for k in ("changed_files","test_failures","previous_failures","build_duration","cpu_usage","coverage")]]
            score = float(model.predict_proba(features)[0][1] * 100)
    except Exception:
        pass
    score = max(2, min(99, round(score)))
    level = "LOW" if score < 35 else "MEDIUM" if score < 70 else "HIGH"
    if not reasons:
        reasons.append("No major risk signals detected in the supplied pipeline metrics.")
    return {"risk_score": score, "risk_level": level, "reasons": reasons}
