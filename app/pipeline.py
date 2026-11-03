import json, random, shutil, time
from datetime import datetime
from pathlib import Path
from ml.predict import predict_risk

ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = ROOT / "data" / "state.json"
DEPLOY_DIR = ROOT / "deployments"

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"runs": [], "active_version": None, "previous_version": None}

def save_state(state):
    STATE_FILE.parent.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))

def run_pipeline(payload):
    # Simulated CI metrics: in a real deployment these come from Jenkins/build tools.
    metrics = {
        "changed_files": int(payload.get("changed_files", 8)),
        "test_failures": int(payload.get("test_failures", 0)),
        "previous_failures": int(payload.get("previous_failures", 0)),
        "build_duration": int(payload.get("build_duration", 75)),
        "cpu_usage": int(payload.get("cpu_usage", 45)),
        "coverage": int(payload.get("coverage", 85)),
    }
    prediction = predict_risk(metrics)
    run_id = int(time.time() * 1000)
    version = f"release-{run_id}"
    checks_passed = metrics["test_failures"] == 0
    status = "BLOCKED" if (not checks_passed or prediction["risk_score"] >= 70) else "DEPLOYED"
    rollback = False
    state = load_state()

    if status == "DEPLOYED":
        DEPLOY_DIR.mkdir(exist_ok=True)
        version_dir = DEPLOY_DIR / version
        version_dir.mkdir(exist_ok=True)
        (version_dir / "release.txt").write_text(
            f"{version}\nCreated: {datetime.now().isoformat()}\nRisk: {prediction['risk_score']}%"
        )
        state["previous_version"] = state.get("active_version")
        state["active_version"] = version
    elif state.get("active_version") and payload.get("simulate_health_failure") == "yes":
        # Demonstration rollback: restore the previous known-good release.
        failed_version = version
        restored = state.get("previous_version") or state.get("active_version")
        state["active_version"] = restored
        rollback = True
        status = "ROLLED BACK"
        prediction["reasons"].append("Post-deployment health check failed; previous stable release restored.")

    run = {
        "id": run_id, "version": version, "created_at": datetime.now().strftime("%d %b %Y, %H:%M:%S"),
        "status": status, "risk_score": prediction["risk_score"], "risk_level": prediction["risk_level"],
        "reasons": prediction["reasons"], "metrics": metrics, "rollback": rollback
    }
    state["runs"].insert(0, run)
    state["runs"] = state["runs"][:30]
    save_state(state)
    return run, state

def clear_history():
    save_state({"runs": [], "active_version": None, "previous_version": None})
    if DEPLOY_DIR.exists():
        shutil.rmtree(DEPLOY_DIR)
