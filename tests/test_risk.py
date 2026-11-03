from ml.predict import predict_risk

def test_low_risk_for_healthy_metrics():
    result = predict_risk({
        "changed_files": 5, "test_failures": 0, "previous_failures": 0,
        "build_duration": 50, "cpu_usage": 35, "coverage": 95
    })
    assert result["risk_level"] == "LOW"
    assert result["risk_score"] < 35

def test_test_failures_raise_risk():
    result = predict_risk({
        "changed_files": 10, "test_failures": 3, "previous_failures": 2,
        "build_duration": 100, "cpu_usage": 45, "coverage": 90
    })
    assert result["risk_score"] >= 70
