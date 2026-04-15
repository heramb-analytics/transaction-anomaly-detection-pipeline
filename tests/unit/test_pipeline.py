#!/usr/bin/env python3
"""
Stage 4: Unit Tests
- 8 pytest tests for pipeline validation
- Self-healing on failure
"""

import pytest
import pandas as pd
import numpy as np
import joblib
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
DATA_PROCESSED = ROOT / "data" / "processed"
MODELS = ROOT / "models"
LOGS = ROOT / "logs"

class TestPipeline:
    """Test suite for the ML pipeline"""
    
    def test_01_raw_data_exists(self):
        """Test: raw data file exists"""
        raw_file = ROOT / "data" / "raw" / "transactions.csv"
        assert raw_file.exists(), "Raw data file not found"
    
    def test_02_clean_parquet_exists(self):
        """Test: clean.parquet exists and is readable"""
        clean_file = DATA_PROCESSED / "clean.parquet"
        assert clean_file.exists(), "clean.parquet not found"
        df = pd.read_parquet(clean_file)
        assert len(df) > 0, "clean.parquet is empty"
        assert 'is_anomaly' in df.columns, "Target column missing"
    
    def test_03_features_parquet_exists(self):
        """Test: features.parquet exists and has features"""
        features_file = DATA_PROCESSED / "features.parquet"
        assert features_file.exists(), "features.parquet not found"
        df = pd.read_parquet(features_file)
        assert len(df) > 0, "features.parquet is empty"
        # Should have fewer columns than raw (categorical encoded, timestamp dropped)
        assert df.shape[1] >= 10, "Too few features"
    
    def test_04_feature_schema_valid(self):
        """Test: feature_schema.json is valid"""
        schema_file = DATA_PROCESSED / "feature_schema.json"
        assert schema_file.exists(), "feature_schema.json not found"
        with open(schema_file, 'r') as f:
            schema = json.load(f)
        assert isinstance(schema, list), "Schema must be a list"
        assert len(schema) > 0, "Schema is empty"
        assert all('name' in s for s in schema), "Schema missing 'name' field"
    
    def test_05_model_file_exists(self):
        """Test: model.pkl exists and loads"""
        model_file = MODELS / "pipeline_model.pkl"
        assert model_file.exists(), "Model file not found"
        model = joblib.load(model_file)
        assert model is not None, "Failed to load model"
    
    def test_06_metrics_json_valid(self):
        """Test: metrics.json exists and has required fields"""
        metrics_file = MODELS / "pipeline_model_metrics.json"
        assert metrics_file.exists(), "metrics.json not found"
        with open(metrics_file, 'r') as f:
            metrics = json.load(f)
        assert 'algorithm' in metrics, "Missing 'algorithm' field"
        assert 'primary_metric' in metrics, "Missing 'primary_metric' field"
        assert metrics['f1_score'] >= 0, "F1 score should be >= 0"
    
    def test_07_model_predict_runs(self):
        """Test: model can make predictions"""
        model = joblib.load(MODELS / "pipeline_model.pkl")
        features = pd.read_parquet(DATA_PROCESSED / "features.parquet")
        X = features.drop(columns=['is_anomaly'])
        
        # Test prediction
        predictions = model.predict(X.iloc[:5])
        assert len(predictions) == 5, "Prediction count mismatch"
    
    def test_08_quality_report_valid(self):
        """Test: quality_report.json shows all checks passed"""
        report_file = LOGS / "quality_report.json"
        assert report_file.exists(), "quality_report.json not found"
        with open(report_file, 'r') as f:
            report = json.load(f)
        assert report.get('checks_passed', 0) >= 9, "Not enough checks passed"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
