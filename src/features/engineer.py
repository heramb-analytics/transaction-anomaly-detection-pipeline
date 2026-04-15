#!/usr/bin/env python3
"""
Stage 2A: Feature Engineering
- Load cleaned data from data/processed/clean.parquet
- Engineer features: log-transform, scaling, encoding, time-based, interactions
- Save to data/processed/features.parquet and feature_schema.json
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from datetime import datetime

ROOT = Path(__file__).parent.parent.parent
DATA_PROCESSED = ROOT / "data" / "processed"

def engineer_features(df):
    """Apply feature engineering transformations"""
    df = df.copy()
    
    # Parse timestamp
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        df['month'] = df['timestamp'].dt.month
    
    # Log transform of amount (skewed numeric feature)
    df['amount_log'] = np.log1p(df['amount'])
    
    # Z-score normalization of numeric columns
    scaler = StandardScaler()
    numeric_cols = ['amount', 'amount_log']
    if numeric_cols:
        df_scaled = scaler.fit_transform(df[numeric_cols])
        for i, col in enumerate(numeric_cols):
            df[f'{col}_scaled'] = df_scaled[:, i]
    
    # One-hot encoding of categorical columns
    for col in ['merchant_id', 'category']:
        if col in df.columns:
            dummies = pd.get_dummies(df[col], prefix=col, drop_first=True)
            # Convert bool to int for numerical compatibility
            dummies = dummies.astype(int)
            df = pd.concat([df, dummies], axis=1)
    
    # Interaction terms (amount × most correlated feature)
    if 'hour' in df.columns:
        df['amount_hour_interaction'] = df['amount_scaled'] * df['hour']
    
    # Rolling statistics
    df = df.sort_values('timestamp') if 'timestamp' in df.columns else df
    df['amount_rolling_mean'] = df['amount'].rolling(window=3, min_periods=1).mean()
    df['amount_rolling_std'] = df['amount'].rolling(window=3, min_periods=1).std().fillna(0)
    df['amount_rolling_max'] = df['amount'].rolling(window=3, min_periods=1).max()
    
    # Drop original categorical columns that were transformed
    df = df.drop(columns=['transaction_id', 'timestamp', 'merchant_id', 'category'], errors='ignore')
    
    return df

def main():
    print("   Task 2A — Feature Engineering")
    
    # Load clean data
    input_path = DATA_PROCESSED / "clean.parquet"
    df = pd.read_parquet(input_path)
    print(f"   📊 Loaded {len(df)} rows from clean.parquet")
    
    # Engineer features
    df_feat = engineer_features(df)
    print(f"   🔧 Engineered features")
    
    # Save features
    output_path = DATA_PROCESSED / "features.parquet"
    df_feat.to_parquet(output_path, index=False, compression='snappy')
    print(f"   💾 Saved to features.parquet ({len(df_feat.columns)} features)")
    
    # Create feature schema
    schema = []
    for col in df_feat.columns:
        if col != 'is_anomaly':
            schema.append({
                "name": col,
                "dtype": str(df_feat[col].dtype),
                "description": f"Feature: {col}",
                "how_computed": "Engineered from original data"
            })
    
    schema_path = DATA_PROCESSED / "feature_schema.json"
    with open(schema_path, 'w') as f:
        json.dump(schema, f, indent=2)
    print(f"   📋 Schema saved with {len(schema)} features")
    
    return df_feat, schema

if __name__ == "__main__":
    df_feat, schema = main()
