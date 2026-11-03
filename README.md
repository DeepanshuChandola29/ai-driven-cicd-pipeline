# ReleasePilot — AI-Driven CI/CD Pipeline

A beginner-friendly B.Tech project demonstrating an AI-assisted release workflow with an interactive dashboard, risk scoring, pipeline simulation, release history and rollback demonstration.

## Features
- Dark, responsive DevOps dashboard.
- Pipeline simulator with adjustable build/test/CPU/coverage metrics.
- Explainable risk assessment with LOW / MEDIUM / HIGH levels.
- Optional Random Forest model trained from the included demo dataset.
- Risk gate: blocks deployments when test failures exist or risk is 70%+.
- Versioned local release simulation and rollback demonstration.
- Flask JSON API, pytest tests, Docker and a starter Jenkinsfile.

## Requirements
- Python 3.10 or newer (Python 3.11 recommended)
- Windows, macOS or Linux
- Optional: Docker Desktop and Jenkins

## Run locally (Windows PowerShell)
```powershell
cd path\to\ai-driven-cicd-pipeline
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.main
```
Open http://127.0.0.1:5000

If PowerShell blocks activation, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

## Run locally (macOS/Linux)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m app.main
```
Open http://127.0.0.1:5000

## Try the demo
1. Click **Analyze & run pipeline** with default values. It should usually deploy.
2. Increase **Test failures** to 3. The release should be blocked.
3. Set CPU usage above 85 or coverage below 50 to increase risk.
4. First create a successful release, then enable **Simulate post-deployment health failure** and run another low-risk pipeline. The UI demonstrates restoration of the previous stable release.
5. Use **Reset demo data** to clear the local demo state.

## Train the Random Forest model (optional)
The app works immediately with a transparent rule-based risk scorer. To train and activate the included Random Forest model:
```bash
python -m ml.train_model
```
The model is saved to `ml/risk_model.joblib` and automatically loaded by the risk engine. The included CSV is synthetic educational data; replace it with real, anonymized Jenkins build history for meaningful evaluation.

## API
- `GET /api/overview` — recent runs and summary.
- `POST /api/pipeline/run` — run a pipeline simulation.
- `POST /api/reset` — clear local demo history.

Example:
```bash
curl -X POST http://127.0.0.1:5000/api/pipeline/run \
  -H "Content-Type: application/json" \
  -d '{"changed_files":8,"test_failures":0,"previous_failures":0,"build_duration":75,"cpu_usage":45,"coverage":85}'
```

## Docker
```bash
docker compose up --build
```
Open http://localhost:5000

## Jenkins integration
The included `Jenkinsfile` is a starter pipeline for checkout, dependency installation, pytest and Docker image build. To make it a real CI/CD deployment:
1. Push this repository to GitHub.
2. Create a Jenkins Pipeline job connected to the repository.
3. Install/configure Python and Docker on the Jenkins agent.
4. Add a webhook from GitHub to Jenkins.
5. Extend the AI risk gate stage to call this app's API with actual Jenkins build/test metrics.
6. Add environment-specific deployment credentials and a health-check command.
7. Configure rollback to redeploy the last known-good image tag.

**Important:** This package's dashboard simulates a deployment environment locally. The included Jenkinsfile does not deploy to a real production server or execute a live rollback. Those steps require your target host, credentials, registry and deployment platform. Never commit secrets to GitHub.

## Project architecture
GitHub → Jenkins → Build & Test → AI Risk Engine → Risk Gate → Docker Deploy Simulation → Health Check / Rollback → Dashboard

## Suggested academic extension
- Store run history in PostgreSQL instead of JSON.
- Add authentication and role-based access.
- Integrate Prometheus/Grafana for live metrics.
- Add real Jenkins webhook ingestion.
- Use Kubernetes rolling or blue-green deployment.
