#!/usr/bin/env python3
"""
Stage 5: FastAPI Application + Tailwind Dashboard
- REST API endpoints for predictions
- Live status monitoring
- Tailwind CSS dashboard with pre-filled sample values
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import pandas as pd
import joblib
import json
import uuid
from datetime import datetime
from pathlib import Path
import uvicorn

ROOT = Path(__file__).parent.parent.parent
MODELS = ROOT / "models"
DATA_PROCESSED = ROOT / "data" / "processed"

# Load model
model = joblib.load(MODELS / "pipeline_model.pkl")

# Load metrics
with open(MODELS / "pipeline_model_metrics.json", 'r') as f:
    metrics = json.load(f)

# Load feature schema
with open(DATA_PROCESSED / "feature_schema.json", 'r') as f:
    feature_schema = json.load(f)

# Load features for sample values
features_df = pd.read_parquet(DATA_PROCESSED / "features.parquet")

# Get sample values (normal and anomaly)
normal_samples = features_df[features_df['is_anomaly'] == 0]
anomaly_samples = features_df[features_df['is_anomaly'] == 1]

NORMAL_SAMPLE = normal_samples.iloc[0].to_dict() if len(normal_samples) > 0 else features_df.iloc[0].to_dict()
ANOMALY_SAMPLE = anomaly_samples.iloc[0].to_dict() if len(anomaly_samples) > 0 else features_df.iloc[0].to_dict()

# Remove target from samples
NORMAL_SAMPLE.pop('is_anomaly', None)
ANOMALY_SAMPLE.pop('is_anomaly', None)

# Prediction history
predictions_history = []

class PredictRequest(BaseModel):
    """Prediction request schema"""
    amount: float = None
    amount_log: float = None
    amount_scaled: float = None
    hour: int = None
    day_of_week: int = None
    month: int = None
    is_weekend: int = None
    amount_hour_interaction: float = None
    amount_rolling_mean: float = None
    amount_rolling_std: float = None
    amount_log_scaled: float = None
    merchant_id_MCC002: int = 0
    merchant_id_MCC003: int = 0
    category_food: int = 0
    category_retail: int = 0

app = FastAPI(title="Transaction Anomaly Detection Pipeline")

@app.post("/predict")
async def predict(request: PredictRequest):
    """Make a prediction on a transaction"""
    try:
        # Convert request to feature array
        feature_dict = request.dict()
        X = pd.DataFrame([feature_dict])
        
        # Make prediction
        prediction = model.predict(X)[0]
        score = model.score_samples(X)[0]
        
        # Convert: -1 (anomaly) -> "ANOMALY", 1 (normal) -> "NORMAL"
        result = "ANOMALY" if prediction == -1 else "NORMAL"
        confidence = abs(score)
        confidence = max(0, min(1, (confidence - score.min()) / (score.max() - score.min())))
        
        response = {
            "result": result,
            "confidence": round(confidence, 4),
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat()
        }
        
        # Store in history
        predictions_history.append(response)
        if len(predictions_history) > 10:
            predictions_history.pop(0)
        
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": True,
        "model_name": "pipeline_model",
        "version": "1.0"
    }

@app.get("/metrics")
async def get_metrics():
    """Return model metrics"""
    return metrics

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the Tailwind CSS dashboard"""
    
    # Build feature input HTML
    feature_inputs = ""
    for feature in feature_schema:
        fname = feature['name']
        if fname == 'is_anomaly':
            continue
        sample_val = NORMAL_SAMPLE.get(fname, 0)
        input_type = "number" if isinstance(sample_val, (int, float)) else "text"
        step = "0.01" if isinstance(sample_val, float) else "1"
        feature_inputs += f'''
                <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-300 mb-2">{fname.replace('_', ' ').title()}</label>
                    <input
                        type="{input_type}"
                        id="input_{fname}"
                        class="w-full px-4 py-2 bg-gray-700 text-white border border-gray-600 rounded-lg focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
                        placeholder="{input_type} value"
                        step="{step}"
                        value="{sample_val}"
                    />
                </div>
        '''
    
    # Build metrics cards HTML
    metrics_cards = ""
    for key, value in metrics.items():
        if isinstance(value, (int, float)) and key not in ['train_size', 'val_size', 'test_size', 'feature_count']:
            formatted_val = f"{value:.4f}" if isinstance(value, float) else str(value)
            metrics_cards += f'''
            <div class="bg-gray-700 px-6 py-4 rounded-lg border border-gray-600">
                <p class="text-teal-400 text-3xl font-bold">{formatted_val}</p>
                <p class="text-gray-400 text-sm">{key.replace('_', ' ').title()}</p>
            </div>
            '''
    
    # Convert sample dicts to JSON strings for JS
    normal_sample_json = json.dumps(NORMAL_SAMPLE)
    anomaly_sample_json = json.dumps(ANOMALY_SAMPLE)
    history_json = json.dumps(predictions_history)
    
    html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Transaction Anomaly Detection</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white">
    <!-- Header -->
    <div class="bg-gray-800 border-b border-gray-700 py-4 px-6 flex items-center justify-between">
        <div>
            <h1 class="text-2xl font-bold text-teal-400">Transaction Anomaly Detection</h1>
            <p class="text-gray-400 text-sm mt-1">ML Pipeline v1.0</p>
        </div>
        <div class="flex items-center gap-3">
            <div class="flex items-center gap-2">
                <div id="status-dot" class="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                <span id="status-text" class="text-green-400 font-semibold">● RUNNING</span>
            </div>
        </div>
    </div>
    
    <!-- Main Content -->
    <div class="max-w-6xl mx-auto p-8">
        <!-- Prediction Section -->
        <div class="bg-gray-800 border border-gray-700 rounded-lg p-8 mb-8">
            <h2 class="text-xl font-bold mb-6 text-teal-400">🔍 Make Prediction</h2>
            
            <!-- Sample Buttons -->
            <div class="grid grid-cols-2 gap-4 mb-6">
                <button
                    onclick="loadNormalSample()"
                    class="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg font-semibold transition"
                >
                    📊 Load Normal Sample
                </button>
                <button
                    onclick="loadAnomalySample()"
                    class="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg font-semibold transition"
                >
                    🚨 Load Anomaly Sample
                </button>
            </div>
            
            <!-- Feature Form -->
            <div class="grid grid-cols-2 gap-6 mb-6">
                {feature_inputs}
            </div>
            
            <!-- Predict Button -->
            <button
                onclick="makePrediction()"
                class="w-full bg-teal-600 hover:bg-teal-700 px-8 py-3 rounded-lg font-bold text-lg transition"
            >
                🔍 Predict
            </button>
            
            <!-- Result Badge -->
            <div id="result-badge" class="mt-6 hidden p-4 rounded-lg text-center text-xl font-bold">
                <span id="result-text"></span>
            </div>
        </div>
        
        <!-- Metrics Section -->
        <div class="mb-8">
            <h2 class="text-xl font-bold mb-6 text-teal-400">📊 Model Metrics</h2>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                {metrics_cards}
            </div>
        </div>
        
        <!-- Predictions History -->
        <div class="bg-gray-800 border border-gray-700 rounded-lg p-8">
            <h2 class="text-xl font-bold mb-6 text-teal-400">📋 Recent Predictions</h2>
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead class="border-b border-gray-700">
                        <tr>
                            <th class="text-left py-3 px-4 text-gray-400">Timestamp</th>
                            <th class="text-left py-3 px-4 text-gray-400">Result</th>
                            <th class="text-left py-3 px-4 text-gray-400">Confidence</th>
                            <th class="text-left py-3 px-4 text-gray-400">Request ID</th>
                        </tr>
                    </thead>
                    <tbody id="predictions-tbody">
                        <!-- Populated by JS -->
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <script>
        const NORMAL_SAMPLE = {normal_sample_json};
        const ANOMALY_SAMPLE = {anomaly_sample_json};
        
        // Pre-fill with normal sample on load
        window.addEventListener('load', () => {{
            loadNormalSample();
            updateHealth();
            setInterval(updateHealth, 5000);
        }});
        
        function loadNormalSample() {{
            for (const [key, value] of Object.entries(NORMAL_SAMPLE)) {{
                const input = document.getElementById(`input_${{key}}`);
                if (input) input.value = value;
            }}
        }}
        
        function loadAnomalySample() {{
            for (const [key, value] of Object.entries(ANOMALY_SAMPLE)) {{
                const input = document.getElementById(`input_${{key}}`);
                if (input) input.value = value;
            }}
        }}
        
        async function makePrediction() {{
            const data = {{}};
            document.querySelectorAll('input[id^="input_"]').forEach(input => {{
                const key = input.id.replace('input_', '');
                data[key] = parseFloat(input.value) || input.value;
            }});
            
            try {{
                const res = await fetch('/predict', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify(data)
                }});
                const result = await res.json();
                
                const badge = document.getElementById('result-badge');
                const text = document.getElementById('result-text');
                
                if (result.result === 'ANOMALY') {{
                    badge.className = 'mt-6 p-4 rounded-lg text-center text-xl font-bold bg-red-600 text-white';
                    text.textContent = `🚨 ANOMALY — Confidence: ${{(result.confidence * 100).toFixed(1)}}%`;
                }} else {{
                    badge.className = 'mt-6 p-4 rounded-lg text-center text-xl font-bold bg-green-600 text-white';
                    text.textContent = `✅ NORMAL — Confidence: ${{(result.confidence * 100).toFixed(1)}}%`;
                }}
                badge.classList.remove('hidden');
                
                updatePredictionsTable();
            }} catch (e) {{
                alert('Error: ' + e.message);
            }}
        }}
        
        async function updateHealth() {{
            try {{
                const res = await fetch('/health');
                const health = await res.json();
                const dot = document.getElementById('status-dot');
                const text = document.getElementById('status-text');
                if (health.model_loaded) {{
                    dot.classList.add('bg-green-500');
                    dot.classList.remove('bg-red-500');
                    text.classList.add('text-green-400');
                    text.classList.remove('text-red-400');
                }} else {{
                    dot.classList.remove('bg-green-500');
                    dot.classList.add('bg-red-500');
                    text.classList.remove('text-green-400');
                    text.classList.add('text-red-400');
                }}
            }} catch (e) {{
                console.error('Health check failed:', e);
            }}
        }}
        
        function updatePredictionsTable() {{
            // This would fetch from history, but for now we'll just show recent
            const tbody = document.getElementById('predictions-tbody');
            tbody.innerHTML = '<tr><td colspan="4" class="text-center text-gray-400 py-4">Make a prediction to see it here</td></tr>';
        }}
    </script>
</body>
</html>
    '''
    return html

@app.get("/docs", include_in_schema=True)
async def swagger_docs():
    """Redirect to Swagger UI"""
    from fastapi.openapi.utils import get_openapi
    return get_openapi(
        title="Transaction Anomaly Detection API",
        version="1.0.0",
        routes=app.routes,
    )

if __name__ == "__main__":
    print("▶  STAGE 5 STARTING — FastAPI + Dashboard\n")
    print("   Starting uvicorn server...\n")
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="warning"
    )
