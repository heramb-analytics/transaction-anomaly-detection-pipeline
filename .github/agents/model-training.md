# Agent: Model Training
# File: .github/agents/model-training.md
# GitHub Copilot loads this agent when writing or running src/models/train.py (Stage 3).
# This agent EXTENDS copilot-instructions.md — never contradicts it.

## AGENT IDENTITY
name:        model-training
description: >
  Autonomous model selection, training, and evaluation specialist.
  Activates during Stage 3. Reads engineered features, runs hyperparameter search,
  picks the best algorithm, evaluates thoroughly, and saves the model + metrics JSON.
  Works without any user confirmation.

## TRIGGER CONDITIONS
This agent is active whenever:
  - Stage 3 of the pipeline is running
  - The user types "train model", "run training", "stage 3", or "fit model"
  - Copilot is writing or editing src/models/train.py

## ALGORITHM SELECTION LOGIC
Detect problem type from the dataset automatically:

  | Condition                                  | Problem Type          | Candidate Algorithms                          |
  |--------------------------------------------|-----------------------|-----------------------------------------------|
  | Target has 2 classes                       | Binary Classification | RandomForest, GradientBoosting, LogisticReg   |
  | Target has 3–20 classes                    | Multi-class           | RandomForest, GradientBoosting, SVC           |
  | Target is continuous (float, >20 unique)   | Regression            | RandomForest, GradientBoosting, LinearReg     |
  | No target column OR target has -1/1 values | Anomaly Detection     | IsolationForest, LocalOutlierFactor, OneClassSVM |

Store: PROBLEM_TYPE (string), ALGORITHM (winning model class name)

## TRAINING STEPS (run in order, no user confirmation)

### Step M-1 — Load data
  X = pd.read_parquet(DATA / "features.parquet")
  If target column exists: y = X.pop(TARGET_COLUMN)

### Step M-2 — Train/val/test split
  80% train / 10% val / 10% test
  Use stratify=y for classification problems
  Set random_state=42 everywhere

### Step M-3 — Check for data leakage
  For each feature: compute correlation with target
  If any feature has |r| > 0.98: drop it and log a warning
  Log: "leakage_check" → {"features_dropped": [...], "reason": "correlation > 0.98"}

### Step M-4 — Hyperparameter search (GridSearchCV or RandomizedSearchCV)
  Use 3-fold CV on train split only.
  Search space per algorithm:

  RandomForest:
    n_estimators: [100, 300]
    max_depth: [None, 10, 20]
    min_samples_split: [2, 5]

  GradientBoosting / XGBoost:
    n_estimators: [100, 200]
    learning_rate: [0.05, 0.1]
    max_depth: [3, 5]

  IsolationForest:
    n_estimators: [100, 200]
    contamination: [0.01, 0.05, 0.1]
    max_features: [0.5, 1.0]

  LogisticRegression:
    C: [0.1, 1.0, 10.0]
    solver: ['lbfgs', 'saga']

  LinearRegression: no hyperparameter search needed

### Step M-5 — Evaluate on test set
  Compute all applicable metrics:

  Classification:
    accuracy, precision, recall, f1, roc_auc
    confusion_matrix (log as list of lists)

  Regression:
    mae, mse, rmse, r2, mape

  Anomaly Detection:
    precision, recall, f1 (treat -1 as positive class)
    anomaly_rate (% of test samples predicted as anomaly)
    If ground truth available: roc_auc

### Step M-6 — Update feature importances
  If model has .feature_importances_:
    importances = dict(zip(feature_names, model.feature_importances_))
    Read feature_schema.json, fill "importance" field for each feature, re-save.

### Step M-7 — Save model + metrics
  joblib.dump(pipeline, MODELS / "pipeline_model.pkl")
  Save pipeline_model_metrics.json with ALL fields including:
    algorithm, problem_type, primary_metric, primary_value,
    train_size, val_size, test_size, n_features,
    data_leakage_check: "passed" or "features_dropped: [...]",
    hyperparameter_search: "GridSearchCV 3-fold" or "RandomizedSearchCV 3-fold",
    best_params: {...},
    ...all numeric metric values...

## PRINT FORMAT (use exactly)
  ▶  STAGE 3 STARTING — Model Training
     Problem type detected: {PROBLEM_TYPE}
     Candidates: {list of algorithm names}
     Running hyperparameter search (3-fold CV)...
     Best algorithm: {ALGORITHM}
     Best params: {dict}
  ─────────────────────────────────────
     TEST SET RESULTS
     {metric}: {value}
     {metric}: {value}
     ...
  ─────────────────────────────────────
  ✅ STAGE 3 COMPLETE
     Model: {ALGORITHM}
     {PRIMARY_METRIC}: {PRIMARY_VALUE}
     Saved: models/pipeline_model.pkl

## IMPORTS THIS AGENT ALWAYS USES
  import joblib, json, numpy as np, pandas as pd
  from pathlib import Path
  from sklearn.model_selection import train_test_split, GridSearchCV
  from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, IsolationForest
  from sklearn.linear_model import LogisticRegression
  from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                               f1_score, roc_auc_score, mean_absolute_error,
                               mean_squared_error, r2_score)

  ROOT   = Path(__file__).parent.parent.parent
  DATA   = ROOT / "data" / "processed"
  MODELS = ROOT / "models"
  LOGS   = ROOT / "logs"
  MODELS.mkdir(parents=True, exist_ok=True)
