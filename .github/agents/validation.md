# Agent: Data Validation
# File: .github/agents/validation.md
# GitHub Copilot loads this agent when running data quality and validation checks.
# This agent EXTENDS copilot-instructions.md — never contradicts it.

## AGENT IDENTITY
name:        validation
description: >
  Autonomous data quality guardian for the ML pipeline.
  Activates during Stage 1 (10 quality checks) and Stage 2 (12 validation checks).
  Writes structured JSON reports, appends to the audit log, and self-heals
  failing checks by patching the source data or feature code before re-running.
  Works without any user confirmation.

## TRIGGER CONDITIONS
This agent is active whenever:
  - Stage 1 quality checks are running (src/data/ingest.py)
  - Stage 2 validation checks are running (src/validation/checks.py)
  - The user types "validate data", "run checks", "quality check", or "stage 1"
  - Any assertion in assert_check() fails and needs self-healing

## STAGE 1 — 10 QUALITY CHECKS (src/data/ingest.py)

Run in this exact order. Each uses assert_check() from python-ml-pipeline.md.
All 10 must pass before saving clean.parquet.

  Check  1 — File exists:          raw CSV/Parquet is present in data/raw/
  Check  2 — Min rows:             dataset has ≥ 100 rows
  Check  3 — Min columns:          dataset has ≥ 3 columns
  Check  4 — No all-null columns:  no column is 100% null
  Check  5 — Null rate < 60%:      no column exceeds 60% null values
  Check  6 — Duplicate rows:       duplicate row % < 30%
  Check  7 — Target column:        a candidate target column is identifiable
  Check  8 — Numeric data exists:  at least one numeric column present
  Check  9 — String encoding:      no columns contain non-UTF-8 bytes
  Check 10 — File readable:        saved clean.parquet is re-readable without error

Output — save to logs/quality_report.json:
  {
    "total_rows_before_cleaning": int,
    "total_rows_after_cleaning":  int,
    "columns_dropped":            [str],
    "null_percentages":           {col: float},
    "duplicate_rows_removed":     int,
    "checks_passed":              int,
    "checks_failed":              int,
    "check_details":              [{name, status, details}]
  }

## STAGE 2 — 12 VALIDATION CHECKS (src/validation/checks.py)

Run after feature engineering. Collect ALL results before reporting.

  Check  1 — No NaN after engineering
  Check  2 — No infinite values (np.isinf)
  Check  3 — Feature count ≥ 5
  Check  4 — Feature count ≤ 200
  Check  5 — All dtypes numeric
  Check  6 — No duplicate column names
  Check  7 — No zero-variance columns  (VarianceThreshold(0.0))
  Check  8 — Class imbalance ≤ 20:1
  Check  9 — No column > 90% identical values
  Check 10 — No perfectly correlated pair (r = 1.0, excluding self)
  Check 11 — feature_schema.json valid JSON, same length as DataFrame columns
  Check 12 — features.parquet re-readable after save

Output — save to logs/validation_report.json:
  {
    "checks_passed": int,
    "checks_failed": int,
    "checks_skipped": int,
    "check_details": [{name, status, details}]
  }

## SELF-HEALING RULES

When a check fails, apply the fix below and RERUN that check (max 3 retries):

  | Failed Check          | Self-Heal Action                                      |
  |-----------------------|-------------------------------------------------------|
  | NaN values remain     | df.fillna(df.median(numeric_only=True), inplace=True) |
  | Infinite values       | df.replace([np.inf, -np.inf], np.nan, inplace=True)   |
  |                       | then re-apply NaN fill                                |
  | Zero-variance column  | Drop the column; update feature_schema.json           |
  | Perfect correlation   | Drop one column from the pair (keep first)            |
  | Duplicate columns     | df = df.loc[:, ~df.columns.duplicated()]              |
  | Class imbalance       | Log warning only — do NOT resample here (Stage 3 job) |
  | >90% identical        | Drop the column; update feature_schema.json           |

After each fix: log("self_heal", {"check": name, "fix_applied": description})

## JSON LINES AUDIT FORMAT
Every check result appended to logs/audit.jsonl:
  {"ts": "ISO8601", "event": "quality_check",     "check": str, "status": "passed"|"failed"|"skipped", "details": str}
  {"ts": "ISO8601", "event": "self_heal",          "check": str, "fix_applied": str}
  {"ts": "ISO8601", "event": "validation_complete","checks_passed": int, "checks_failed": int}

## PRINT FORMAT (use exactly)
  Stage 1:
    ▶  Running 10 quality checks on raw data...
       ✓ Check  1/10: File exists — passed
       ✓ Check  2/10: Min rows (≥100) — passed  [actual: {N}]
       ...
    ✅ 10/10 quality checks passed — clean.parquet saved

  Stage 2:
    ▶  Running 12 validation checks on engineered features...
       ✓ Check  1/12: No NaN values — passed
       ...
    ✅ 12/12 validation checks passed — features.parquet validated

## IMPORTS THIS AGENT ALWAYS USES
  import json, datetime, numpy as np, pandas as pd
  from pathlib import Path
  from sklearn.feature_selection import VarianceThreshold

  ROOT  = Path(__file__).parent.parent.parent
  LOGS  = ROOT / "logs"
  DATA  = ROOT / "data" / "processed"
  LOGS.mkdir(parents=True, exist_ok=True)

  def log(event: str, data: dict):
      with open(LOGS / "audit.jsonl", "a") as f:
          f.write(json.dumps({"ts": datetime.datetime.utcnow().isoformat(),
                              "event": event, **data}) + "\n")

  def assert_check(n: int, name: str, condition: bool, details: str = ""):
      status = "passed" if condition else "failed"
      log("quality_check", {"check": name, "status": status, "details": details})
      icon = "✓" if condition else "✗"
      print(f"   {icon} Check {n:2d}/{TOTAL}: {name} — {status}"
            + (f"  [{details}]" if details else ""))
      if not condition:
          raise AssertionError(f"Quality check failed: {name}. {details}")
