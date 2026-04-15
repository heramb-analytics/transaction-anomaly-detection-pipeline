# Python ML Pipeline Coding Standards
# File: .github/skills/python-ml-pipeline.md
# Copilot reads this when writing any src/ Python file.

## File Locations (strict)
  src/data/ingest.py           → data ingestion + 10 quality assertions
  src/features/engineer.py     → feature engineering
  src/features/eda_report.py   → 5 EDA charts (matplotlib)
  src/validation/checks.py     → 12 data validation checks
  src/models/train.py          → model training + evaluation
  src/api/main.py              → FastAPI app + Tailwind dashboard
  src/scheduler/nightly_job.py → APScheduler retrain + drift jobs
  tests/unit/test_pipeline.py  → 8 self-healing unit tests
  tests/e2e/test_api.py        → 6 Playwright e2e tests

## Required Imports Pattern (every src/ file)
  from pathlib import Path
  ROOT    = Path(__file__).parent.parent.parent  # → project root
  DATA    = ROOT / "data" / "processed"
  RAW     = ROOT / "data" / "raw"
  MODELS  = ROOT / "models"
  LOGS    = ROOT / "logs"
  REPORTS = ROOT / "reports"
  FIGS    = ROOT / "reports" / "figures"
  SHOTS   = ROOT / "reports" / "screenshots"

## Code Style Rules
  - Type annotations on all function signatures
  - Google docstrings on all public functions
  - Logging to logs/audit.jsonl (JSON Lines format, append mode)
  - No hardcoded paths — always use ROOT-relative Path objects
  - One class or function per logical concern

## JSON Lines Logging Pattern
  import json, datetime
  def log(event: str, data: dict):
      with open(LOGS / "audit.jsonl", "a") as f:
          f.write(json.dumps({"ts": datetime.datetime.utcnow().isoformat(),
                              "event": event, **data}) + "\n")

## Quality Assertions Pattern (Stage 1)
  def assert_check(name: str, condition: bool, details: str = ""):
      status = "passed" if condition else "failed"
      log("quality_check", {"check": name, "status": status, "details": details})
      if not condition:
          raise AssertionError(f"Quality check failed: {name}. {details}")
      print(f"   ✓ Check {n}/10: {name} — passed")

## Model Save Pattern (Stage 3)
  import joblib, json
  joblib.dump(pipeline, MODELS / "pipeline_model.pkl")
  with open(MODELS / "pipeline_model_metrics.json", "w") as f:
      json.dump({
          "algorithm": ALGORITHM_NAME,
          "problem_type": PROBLEM_TYPE,
          "primary_metric": PRIMARY_METRIC_NAME,
          "train_size": len(X_train),
          "test_size": len(X_test),
          **{k: float(v) for k, v in all_metrics.items()}
      }, f, indent=2)

## FastAPI Response Pattern (Stage 5)
  @app.post("/predict")
  def predict(data: dict) -> dict:
      import uuid, datetime
      result = model.predict([list(data.values())])[0]
      score  = float(model.decision_function([list(data.values())])[0])
      return {
          "result":     "ANOMALY" if result == -1 else "NORMAL",
          "confidence": round(abs(score), 4),
          "request_id": str(uuid.uuid4()),
          "timestamp":  datetime.datetime.utcnow().isoformat()
      }

## Self-Healing Test Pattern (Stage 4)
  Tests fix the SOURCE file on failure — not the test.
  All tests import from src.* using proper package imports.
  conftest.py in tests/ adds ROOT to sys.path.
