#!/usr/bin/env python3
"""
Stage 3: Model Training
- Load engineered features
- Split into train/val/test (70/15/15)
- Train isolation forest for anomaly detection
- Save model and metrics
"""

import pandas as pd
import numpy as np
import json
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import IsolationForest
from sklearn.metrics import (
    precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, confusion_matrix
)

ROOT = Path(__file__).parent.parent.parent
DATA_PROCESSED = ROOT / "data" / "processed"
MODELS = ROOT / "models"
LOGS = ROOT / "logs"

MODELS.mkdir(parents=True, exist_ok=True)
LOGS.mkdir(parents=True, exist_ok=True)

def train_model():
    """Train anomaly detection model"""
    print("   📊 Loading features...")
    df = pd.read_parquet(DATA_PROCESSED / "features.parquet")
    
    X = df.drop(columns=['is_anomaly'])
    y = df['is_anomaly']
    
    print("   🔀 Splitting data (70/15/15 train/val/test)...")
    
    # First split: 70% train, 30% temp (for val+test)
    try:
        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y, test_size=0.3, random_state=42, stratify=y
        )
    except ValueError:
        # If stratification fails (too few samples), do simple random split
        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y, test_size=0.3, random_state=42
        )
    
    # Second split: split temp into half for val and test
    try:
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
        )
    except ValueError:
        # If stratification fails, do simple random split
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, test_size=0.5, random_state=42
        )
    
    # Verify no data leakage
    train_idx = set(X_train.index)
    val_idx = set(X_val.index)
    test_idx = set(X_test.index)
    
    overlap_train_test = len(train_idx & test_idx)
    overlap_train_val = len(train_idx & val_idx)
    overlap_val_test = len(val_idx & test_idx)
    
    print(f"   ✓ Data leakage check:")
    print(f"     - Train ∩ Test: {overlap_train_test} rows (must be 0)")
    print(f"     - Train ∩ Val:  {overlap_train_val} rows (must be 0)")
    print(f"     - Val ∩ Test:   {overlap_val_test} rows (must be 0)")
    
    assert overlap_train_test == 0 and overlap_train_val == 0 and overlap_val_test == 0
    print(f"   ✅ Zero data leakage confirmed\n")
    
    print("   🤖 Training Isolation Forest...")
    model = IsolationForest(
        n_estimators=100,
        contamination=0.1,  # Expect ~10% anomalies
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train)
    print("   ✅ Model trained")
    
    # Predictions
    print("\n   📈 Evaluating model...")
    y_pred_train = model.predict(X_train)
    y_pred_val = model.predict(X_val)
    y_pred_test = model.predict(X_test)
    
    # Convert predictions: -1 (anomaly) -> 1, 1 (normal) -> 0
    y_pred_test_binary = (y_pred_test == -1).astype(int)
    
    # Decision scores for AUC
    y_scores = model.score_samples(X_test)
    
    # Calculate metrics
    precision = precision_score(y_test, y_pred_test_binary, zero_division=0)
    recall = recall_score(y_test, y_pred_test_binary, zero_division=0)
    f1 = f1_score(y_test, y_pred_test_binary, zero_division=0)
    
    try:
        auc_roc = roc_auc_score(y_test, y_scores)
    except:
        auc_roc = 0.5
    
    anomaly_rate = (y_pred_test_binary == 1).sum() / len(y_pred_test_binary)
    
    print(f"   ✓ Precision: {precision:.4f}")
    print(f"   ✓ Recall:    {recall:.4f}")
    print(f"   ✓ F1 Score:  {f1:.4f}")
    print(f"   ✓ AUC-ROC:   {auc_roc:.4f}")
    print(f"   ✓ Anomaly rate (test): {anomaly_rate:.2%}")
    
    # Save model
    model_path = MODELS / "pipeline_model.pkl"
    joblib.dump(model, model_path)
    print(f"\n   💾 Model saved to {model_path.name}")
    
    # Save metrics
    metrics = {
        "algorithm": "IsolationForest",
        "problem_type": "anomaly_detection",
        "primary_metric": "f1_score",
        "primary_value": f1,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "auc_roc": auc_roc,
        "anomaly_rate": anomaly_rate,
        "train_size": len(X_train),
        "val_size": len(X_val),
        "test_size": len(X_test),
        "feature_count": X_train.shape[1],
        "best_params": {
            "n_estimators": 100,
            "contamination": 0.1,
            "random_state": 42
        }
    }
    
    metrics_path = MODELS / "pipeline_model_metrics.json"
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"   📊 Metrics saved to {metrics_path.name}")
    
    return model, metrics

if __name__ == "__main__":
    model, metrics = train_model()
    print(f"\n✅ STAGE 3 COMPLETE — IsolationForest · f1_score: {metrics['f1_score']:.4f}\n")
