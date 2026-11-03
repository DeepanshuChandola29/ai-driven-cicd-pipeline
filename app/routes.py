from flask import Blueprint, render_template, request, jsonify
from app.pipeline import load_state, run_pipeline, clear_history

bp = Blueprint("main", __name__)

@bp.get("/")
def dashboard():
    state = load_state()
    runs = state["runs"]
    total = len(runs)
    deployed = sum(r["status"] == "DEPLOYED" for r in runs)
    failed = sum(r["status"] == "BLOCKED" for r in runs)
    rolled = sum(r["status"] == "ROLLED BACK" for r in runs)
    avg_risk = round(sum(r["risk_score"] for r in runs) / total) if total else 0
    return render_template("index.html", runs=runs, stats={
        "total": total, "deployed": deployed, "failed": failed, "rolled": rolled,
        "avg_risk": avg_risk, "active": state.get("active_version") or "No active release"
    })

@bp.post("/api/pipeline/run")
def pipeline_run():
    run, state = run_pipeline(request.get_json(silent=True) or {})
    return jsonify({"run": run, "active_version": state.get("active_version")})

@bp.get("/api/overview")
def overview():
    state = load_state()
    runs = state["runs"]
    return jsonify({
        "runs": runs,
        "active_version": state.get("active_version"),
        "total": len(runs),
        "success": sum(r["status"] == "DEPLOYED" for r in runs),
        "blocked": sum(r["status"] == "BLOCKED" for r in runs),
        "rollback": sum(r["rollback"] for r in runs)
    })

@bp.post("/api/reset")
def reset():
    clear_history()
    return jsonify({"ok": True})
