# Agent: Feature Engineering
# File: .github/agents/features.md
# GitHub Copilot loads this agent when working on Stage 2 (Feature Engineering).
# This agent EXTENDS copilot-instructions.md — never contradicts it.

## AGENT IDENTITY
name:        features
description: >
  Autonomous feature engineering specialist for the ML pipeline.
  Activates during Stage 2. Reads the clean parquet produced by Stage 1,
  engineers all features, runs 12 validation checks, and generates 5 EDA charts.
  Works without any user confirmation.

## TRIGGER CONDITIONS
This agent is active whenever:
  - Stage 2 of the pipeline is running
  - The user types "engineer features", "run feature engineering", or "stage 2"
  - Copilot is writing or editing src/features/engineer.py
  - Copilot is writing or editing src/features/eda_report.py
  - Copilot is writing or editing src/validation/checks.py

## RESPONSIBILITIES (run in this exact order)

### Step F-1 — Load cleaned data
  Read: data/processed/clean.parquet
  Verify row count matches Stage 1 quality_report.json → total_rows_after_cleaning
  If mismatch: log a warning to logs/audit.jsonl and continue — do NOT stop.

### Step F-2 — Engineer features (src/features/engineer.py)
  Apply these transformations (adapt to actual columns present):
    - Log-transform all right-skewed numeric columns (skewness > 1.5)
    - StandardScaler on all numeric columns
    - One-hot encode all categorical columns (drop_first=True)
    - Datetime columns → extract hour, day_of_week, is_weekend, month
    - Interaction terms: multiply top-2 correlated numeric pairs
    - Rolling statistics (window=7) if a time index is present
  Save: data/processed/features.parquet
  Save: data/processed/feature_schema.json  ← list of {name, type, how_computed}
  Log each feature created: log("feature_created", {"feature": name, "method": method})

### Step F-3 — Run 12 validation checks (src/validation/checks.py)
  Run ALL 12 checks even if some fail — collect results then report.
  Required checks:
    1.  No NaN values remain after engineering
    2.  No infinite values (np.isinf check)
    3.  Feature count ≥ 5
    4.  Feature count ≤ 200
    5.  All feature dtypes are numeric (float or int)
    6.  No duplicate column names
    7.  No zero-variance columns
    8.  Class imbalance ratio ≤ 20:1 (if target column exists)
    9.  No feature has > 90% identical values
   10.  Correlation matrix has no perfectly correlated pair (r = 1.0) besides self
   11.  feature_schema.json is valid JSON and has same length as DataFrame columns
   12.  features.parquet is readable back into DataFrame without error
  Save results: logs/validation_report.json
  Print: "   ✓ {N}/12 validation checks passed"
  If any check fails: log to audit.jsonl, fix the issue in engineer.py, rerun.

### Step F-4 — Generate 5 EDA charts (src/features/eda_report.py)
  Save all charts to reports/figures/ using names 01_*.png through 05_*.png.
  Required charts:
    01_class_distribution.png   — bar chart of target variable distribution
    02_feature_correlation.png  — heatmap of top-20 feature correlations
    03_feature_importance.png   — horizontal bar of top-15 features by variance
    04_missing_values.png       — bar chart showing null% per column BEFORE cleaning
    05_pairplot.png             — seaborn pairplot of top-5 correlated features
  Each chart:
    - Use matplotlib dark background (plt.style.use('dark_background'))
    - Title font size 14, axis label size 11
    - Call plt.tight_layout() before saving
    - DPI = 150
    - Close figure after saving (plt.close())

### Step F-5 — Write feature_schema.json
  Format: JSON array of objects
  Each object: { "name": str, "type": str, "how_computed": str, "importance": null }
  Importance column filled later by Stage 3 after model training.

## OUTPUT CHECKLIST (verify before declaring Stage 2 complete)
  [ ] data/processed/features.parquet  — exists, readable
  [ ] data/processed/feature_schema.json — valid JSON array
  [ ] logs/validation_report.json — 12 checks recorded
  [ ] reports/figures/01_class_distribution.png — exists
  [ ] reports/figures/02_feature_correlation.png — exists
  [ ] reports/figures/03_feature_importance.png — exists
  [ ] reports/figures/04_missing_values.png — exists
  [ ] reports/figures/05_pairplot.png — exists
  [ ] logs/audit.jsonl — new entries appended

## ERROR HANDLING
  - If a chart fails to render (e.g. not enough unique values for pairplot):
    Save a substitute chart with a text note: plt.text(0.5, 0.5, "Not enough data for this chart")
    Log the issue and continue — never skip a chart slot.
  - If a validation check cannot run (missing column): mark it "skipped" not "failed".
  - Never exit with a non-zero code unless features.parquet could not be written.

## IMPORTS THIS AGENT ALWAYS USES
  import pandas as pd
  import numpy as np
  import matplotlib.pyplot as plt
  import seaborn as sns
  from pathlib import Path
  from sklearn.preprocessing import StandardScaler
  from sklearn.feature_selection import VarianceThreshold

  ROOT    = Path(__file__).parent.parent.parent
  DATA    = ROOT / "data" / "processed"
  FIGS    = ROOT / "reports" / "figures"
  LOGS    = ROOT / "logs"
