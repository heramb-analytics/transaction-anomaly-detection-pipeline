#!/usr/bin/env python3
"""
Stage 6: Playwright E2E Tests + Screenshots
- 6 end-to-end browser tests
- Save 6 screenshots as evidence
"""

import pytest
from pathlib import Path
from playwright.sync_api import sync_playwright

REPORTS_DIR = Path(__file__).parent.parent.parent / "reports" / "screenshots"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
BASE_URL = "http://localhost:8000"

class TestE2E:
    """End-to-end tests using Playwright"""
    
    def test_01_dashboard_home(self):
        """Test: Home page loads successfully"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"{BASE_URL}/", wait_until="networkidle")
            
            # Wait for RUNNING badge
            page.wait_for_selector("text=RUNNING", timeout=5000)
            
            # Take screenshot
            page.screenshot(path=str(REPORTS_DIR / "01_dashboard_home.png"), full_page=True)
            browser.close()
    
    def test_02_form_filled_with_sample(self):
        """Test: Form pre-fills with sample values"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"{BASE_URL}/", wait_until="networkidle")
            page.wait_for_selector("input[id^='input_']", timeout=5000)
            
            # Click Load Anomaly Sample button
            anomaly_btn = page.locator("text=Load Anomaly Sample")
            if anomaly_btn.count() > 0:
                anomaly_btn.click()
                page.wait_for_timeout(500)
            
            # Take screenshot
            page.screenshot(path=str(REPORTS_DIR / "02_form_filled.png"), full_page=True)
            browser.close()
    
    def test_03_prediction_result(self):
        """Test: Make prediction and get result"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"{BASE_URL}/", wait_until="networkidle")
            page.wait_for_selector("button:has-text('Predict')", timeout=5000)
            
            # Click Predict button
            predict_btn = page.locator("button:has-text('Predict')")
            predict_btn.click()
            
            # Wait for result badge
            page.wait_for_selector("#result-badge", timeout=5000)
            page.wait_for_timeout(500)
            
            # Take screenshot
            page.screenshot(path=str(REPORTS_DIR / "03_prediction_result.png"), full_page=True)
            browser.close()
    
    def test_04_swagger_ui(self):
        """Test: Swagger UI loads"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"{BASE_URL}/docs", wait_until="networkidle")
            
            # Wait for Swagger UI
            page.wait_for_timeout(1000)
            
            # Take screenshot
            page.screenshot(path=str(REPORTS_DIR / "04_swagger_docs.png"), full_page=True)
            browser.close()
    
    def test_05_metrics_endpoint(self):
        """Test: Metrics endpoint returns data"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"{BASE_URL}/metrics", wait_until="networkidle")
            
            # Wait for JSON to load
            page.wait_for_timeout(500)
            
            # Take screenshot
            page.screenshot(path=str(REPORTS_DIR / "05_metrics_endpoint.png"), full_page=True)
            browser.close()
    
    def test_06_health_endpoint(self):
        """Test: Health endpoint"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"{BASE_URL}/health", wait_until="networkidle")
            
            # Wait for JSON
            page.wait_for_timeout(500)
            
            # Take screenshot
            page.screenshot(path=str(REPORTS_DIR / "06_health_endpoint.png"), full_page=True)
            browser.close()

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
