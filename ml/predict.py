
# Explainable demo risk model.
# Uses a trained model if available; otherwise uses a weighted score.

from pathlib import Path
import joblib

MODEL_PATH = Path(__file__).resolve().parent / "risk_model.joblib"


def predict_risk(metrics):
    reasons = []
    score = 0

    # Automated test failures
    if metrics["test_failures"] > 0:
        score += min(60, metrics["test_failures"] * 20)
        reasons.append(
            f'{metrics["test_failures"]} automated test failure(s) detected.'
        )

    # Previous pipeline failures
    if metrics["previous_failures"] > 1:
        score += min(25, (metrics["previous_failures"] - 1) * 10)
        reasons.append(
            "Recent pipeline history contains repeated failures."
        )

    # High CPU usage
    if metrics["cpu_usage"] > 75:
        score += min(15, (metrics["cpu_usage"] - 75) * 0.8)
        reasons.append(
            "High CPU utilization may affect runtime stability."
        )

    # Low test coverage
    if metrics["coverage"] < 70:
        score += min(15, (70 - metrics["coverage"]) * 0.8)
        reasons.append(
            "Test coverage is below the recommended 70% threshold."
        )

    # Large code changes
    if metrics["changed_files"] > 20:
        score += min(10, (metrics["changed_files"] - 20) * 0.5)
        reasons.append(
            "Large change size increases release complexity."
        )

    # Long build duration
    if metrics["build_duration"] > 180:
        score += 8
        reasons.append("Build duration is unusually high.")

    # Use trained model if available
    try:
        if MODEL_PATH.exists():
            model = joblib.load(MODEL_PATH)

            features = [[
                metrics[k] for k in (
                    "changed_files",
                    "test_failures",
                    "previous_failures",
                    "build_duration",
                    "cpu_usage",
                    "coverage"
                )
            ]]

            score = float(model.predict_proba(features)[0][1] * 100)

    except Exception:
        pass

    score = max(2, min(99, round(score)))

    level = (
        "LOW" if score < 35
        else "MEDIUM" if score < 70
        else "HIGH"
    )

    if not reasons:
        reasons.append(
            "No major risk signals detected in the supplied pipeline metrics."
        )

    return {
        "risk_score": score,
        "risk_level": level,
        "reasons": reasons
    }
