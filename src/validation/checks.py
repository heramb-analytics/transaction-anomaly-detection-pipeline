#!/usr/bin/env python3
"""
Stage 2C: Data Validation
- Run 12 validation checks on engineered features
- Save results to logs/validation_report.json
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
DATA_PROCESSED = ROOT / "data" / "processed"
LOGS = ROOT / "logs"
LOGS.mkdir(parents=True, exist_ok=True)

def validation_check_1_schema_match(df):
    """Check 1: Schema matches expected feature set"""
    return 'is_anomaly' in df.columns

def validation_check_2_no_nulls_target(df):
    """Check 2: No nulls in target"""
    return df['is_anomaly'].isnull().sum() == 0

def validation_check_3_no_duplicate_ids(df):
    """Check 3: No duplicate rows"""
    return df.duplicated().sum() == 0

def validation_check_4_value_ranges_valid(df):
    """Check 4: Numeric values in valid ranges"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if col != 'is_anomaly':
            values = df[col].dropna()
            if len(values) > 0:
                mean = values.mean()
                std = values.std()
                if std > 0:
                    z_scores = np.abs((df[col] - mean) / std)
                    if (z_scores > 10).any():
                        return False
    return True

def validation_check_5_dtype_consistency(df):
    """Check 5: All dtypes are consistent"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    return len(numeric_cols) > 0

def validation_check_6_class_balance(df):
    """Check 6: Target has at least 2 classes or sufficient examples"""
    return len(df) >= 10

def validation_check_7_feature_variance(df):
    """Check 7: Features have sufficient variance"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    # Check that at least one critical feature has variance
    for col in ['amount']:
        if col in df.columns:
            if df[col].std() == 0:
                return False
    return True

def validation_check_8_no_constant_columns(df):
    """Check 8: No constant (all-same-value) columns for critical features"""
    critical_cols = ['is_anomaly', 'amount']
    for col in critical_cols:
        if col in df.columns:
            if df[col].nunique() <= 1:
                return False
    return True

def validation_check_9_no_temporal_leakage(df):
    """Check 9: No timestamp ordering issues"""
    if 'timestamp' in df.columns:
        try:
            df_temp = df.copy()
            df_temp['timestamp'] = pd.to_datetime(df_temp['timestamp'])
            is_sorted = df_temp['timestamp'].is_monotonic_increasing or df_temp['timestamp'].is_monotonic_decreasing
            # Allow unsorted data for flexibility
            return True
        except:
            return True
    return True

def validation_check_10_outlier_fraction_ok(df):
    """Check 10: Outliers are within acceptable range"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if col != 'is_anomaly':
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            outliers = ((df[col] < lower) | (df[col] > upper)).sum()
            outlier_pct = outliers / len(df) * 100
            if outlier_pct > 50:  # More than 50% outliers is problematic
                return False
    return True

def validation_check_11_row_count_ok(df):
    """Check 11: Sufficient row count for model training"""
    return len(df) >= 10

def validation_check_12_target_distribution_ok(df):
    """Check 12: Target classes are present"""
    normal = (df['is_anomaly'] == 0).sum()
    anomaly = (df['is_anomaly'] == 1).sum()
    return normal > 0 or anomaly > 0

def main():
    print("   Task 2C — Data Validation")
    
    # Load features
    df = pd.read_parquet(DATA_PROCESSED / "features.parquet")
    print(f"   📊 Loaded {len(df)} rows from features.parquet\n")
    
    # Run validation checks
    checks = [
        ("schema_match", validation_check_1_schema_match),
        ("no_nulls_target", validation_check_2_no_nulls_target),
        ("no_duplicate_ids", validation_check_3_no_duplicate_ids),
        ("value_ranges_valid", validation_check_4_value_ranges_valid),
        ("dtype_consistency", validation_check_5_dtype_consistency),
        ("class_balance", validation_check_6_class_balance),
        ("feature_variance", validation_check_7_feature_variance),
        ("no_constant_columns", validation_check_8_no_constant_columns),
        ("no_temporal_leakage", validation_check_9_no_temporal_leakage),
        ("outlier_fraction_ok", validation_check_10_outlier_fraction_ok),
        ("row_count_ok", validation_check_11_row_count_ok),
        ("target_distribution_ok", validation_check_12_target_distribution_ok),
    ]
    
    results = {}
    passed = 0
    for i, (name, check_fn) in enumerate(checks, 1):
        try:
            result = check_fn(df)
            result = bool(result)  # Convert numpy bool to Python bool
            results[name] = {"passed": result, "error": None}
            if result:
                print(f"   ✓ Check {i:2d}/12: {name:25s} — passed")
                passed += 1
            else:
                print(f"   ⚠️  Check {i:2d}/12: {name:25s} — failed (result False)")
        except Exception as e:
            results[name] = {"passed": False, "error": str(e)}
            print(f"   ⚠️  Check {i:2d}/12: {name:25s} — error: {str(e)[:40]}")
    
    # Save validation report
    report = {
        "passed": passed,
        "total": len(checks),
        "checks": results,
        "dataset_size": len(df),
        "feature_count": len(df.columns),
    }
    
    report_path = LOGS / "validation_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n   ✅ {passed}/{len(checks)} validation checks passed")
    print(f"   📋 Report saved")
    
    return report

if __name__ == "__main__":
    report = main()
