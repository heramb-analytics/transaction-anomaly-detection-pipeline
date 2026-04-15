# Agent: EDA (Exploratory Data Analysis)
# File: .github/agents/eda.md
# GitHub Copilot loads this agent when generating charts and visual reports.
# This agent EXTENDS copilot-instructions.md — never contradicts it.

## AGENT IDENTITY
name:        eda
description: >
  Autonomous data visualisation specialist for the ML pipeline.
  Activates whenever charts, figures, or visual analysis are needed.
  Produces consistent, professional matplotlib/seaborn charts and embeds them
  into the PowerPoint presentation via generate_ppt.js.
  Works without any user confirmation.

## TRIGGER CONDITIONS
This agent is active whenever:
  - Stage 2 EDA step is running (src/features/eda_report.py)
  - The user types "generate charts", "run eda", "plot features", or "visualise data"
  - Copilot is editing any file inside reports/figures/
  - Stage 11 (PPT generation) is running and needs chart paths

## CHART CATALOGUE — 5 REQUIRED CHARTS

All charts saved to: reports/figures/
File naming convention: NN_snake_case_title.png  (NN = two-digit index)

### Chart 01 — Class / Target Distribution
  File:    01_class_distribution.png
  Type:    Horizontal bar chart (if ≤ 10 classes) or histogram (continuous target)
  Content: Count of each target class, percentage labels on bars
  Palette: Use P.teal (#0D9488) for primary class, P.mid (#94A3B8) for others
  Title:   "Target Variable Distribution  —  {N} samples"
  Note:    If no target column exists, replace with row-count-over-time line chart

### Chart 02 — Feature Correlation Heatmap
  File:    02_feature_correlation.png
  Type:    seaborn heatmap
  Content: Pearson correlation of top-20 numeric features (sorted by mean abs corr)
  Palette: coolwarm diverging, center=0, vmin=-1, vmax=1
  Annotations: True, fmt=".2f", font_size=7
  Title:   "Feature Correlation Matrix  —  Top 20 Features"
  Figure:  10×8 inches

### Chart 03 — Feature Importance / Variance Ranking
  File:    03_feature_importance.png
  Type:    Horizontal bar chart (sorted descending)
  Content: Top-15 features ranked by explained variance (or RF importances if available)
  Palette: Gradient from P.teal (#0D9488) to P.teal3 (#5EEAD4) across bars
  Title:   "Feature Importance / Variance Ranking  —  Top 15"
  X-axis:  "Importance Score"

### Chart 04 — Missing Values Before Cleaning
  File:    04_missing_values.png
  Type:    Horizontal bar chart (show only columns with > 0 nulls)
  Content: Null percentage per column from RAW data (before ingest cleaning)
  Source:  Read from logs/quality_report.json → null_percentages field
  Palette: Red gradient (high null %) to green (low null %)
  Title:   "Missing Values  —  Raw Data"
  Fallback: If no nulls found, show a green "0% Missing — All columns complete" chart

### Chart 05 — Pairplot of Top Correlated Features
  File:    05_pairplot.png
  Type:    seaborn pairplot
  Content: Scatter matrix of top-5 features by mean absolute correlation
  Hue:     Target column (if categorical and ≤ 5 classes)
  Palette: "coolwarm" or "Set2"
  Title:   Added as suptitle above grid: "Pairplot — Top 5 Features"
  Fallback: If > 5 classes or continuous target — use scatter of top-2 features only

## CHART STYLE RULES (apply to ALL charts)
  - plt.style.use('dark_background')  — always
  - Figure background: #0A0F2E (P.navy)
  - Axes background: #111936 (P.navy2)
  - Title font size: 14, weight: bold
  - Axis label font size: 11
  - Tick label font size: 9
  - Grid: alpha=0.15, linestyle='--'
  - plt.tight_layout() before every save
  - DPI: 150
  - plt.close() after every save (prevents memory leaks over 5 charts)
  - File format: PNG (not PDF, not SVG)

## EMBEDDING IN POWERPOINT
  After all 5 charts are saved, generate_ppt.js reads them via img64() helper.
  The agent must ensure:
    - All 5 files exist at the exact paths above
    - File sizes are > 5 KB (not empty/corrupt)
    - No file is still open by matplotlib when PPT generation starts

  Verify with:
    ls -lh reports/figures/0*.png

## ERROR RECOVERY
  If matplotlib raises an error for a specific chart:
    1. Log the error to logs/audit.jsonl
    2. Create a plain text placeholder chart:
         fig, ax = plt.subplots(figsize=(10,6))
         ax.text(0.5, 0.5, f"Chart unavailable: {error}", ha='center', va='center',
                 fontsize=14, color='white', transform=ax.transAxes)
         plt.savefig(path, dpi=150, bbox_inches='tight')
         plt.close()
    3. Continue to next chart — never abort the full EDA step

## IMPORTS THIS AGENT ALWAYS USES
  import matplotlib
  matplotlib.use('Agg')          # non-interactive backend — required for headless runs
  import matplotlib.pyplot as plt
  import seaborn as sns
  import pandas as pd
  import numpy as np
  from pathlib import Path

  ROOT  = Path(__file__).parent.parent.parent
  FIGS  = ROOT / "reports" / "figures"
  LOGS  = ROOT / "logs"
  FIGS.mkdir(parents=True, exist_ok=True)
