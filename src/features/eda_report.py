#!/usr/bin/env python3
"""
Stage 2B: EDA Report
- Generate 5 exploratory data analysis charts
- Save to reports/figures/
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
DATA_PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "reports" / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

def plot_target_distribution(df):
    """Chart 1: Target distribution"""
    fig, ax = plt.subplots(figsize=(10, 6))
    counts = df['is_anomaly'].value_counts()
    colors = ['#2ecc71', '#e74c3c']
    ax.bar(counts.index, counts.values, color=colors, alpha=0.7, edgecolor='black')
    ax.set_xlabel('Transaction Type')
    ax.set_ylabel('Count')
    ax.set_title('Target Distribution - Normal vs Anomaly', fontsize=14, fontweight='bold')
    ax.set_xticklabels(['Normal', 'Anomaly'])
    for i, v in enumerate(counts.values):
        ax.text(i, v + 1, str(v), ha='center', fontweight='bold')
    plt.tight_layout()
    plt.savefig(FIGURES / "01_target_distribution.png", dpi=150)
    plt.close()
    print("   📊 Chart 1/5: 01_target_distribution.png")

def plot_feature_correlations(df):
    """Chart 2: Feature correlations heatmap"""
    fig, ax = plt.subplots(figsize=(10, 8))
    numeric_df = df.select_dtypes(include=[np.number])
    corr = numeric_df.corr()
    # Only show top 10 correlations with target
    if 'is_anomaly' in corr.columns:
        top_features = corr['is_anomaly'].abs().sort_values(ascending=False).head(11).index.tolist()
        corr_subset = corr.loc[top_features, top_features]
    else:
        corr_subset = corr.iloc[:10, :10]
    
    sns.heatmap(corr_subset, annot=True, fmt='.2f', cmap='coolwarm', center=0, 
                ax=ax, cbar_kws={'label': 'Correlation'})
    ax.set_title('Feature Correlation Matrix', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(FIGURES / "02_feature_correlations.png", dpi=150)
    plt.close()
    print("   📊 Chart 2/5: 02_feature_correlations.png")

def plot_missing_values(df):
    """Chart 3: Missing values heatmap"""
    fig, ax = plt.subplots(figsize=(10, 6))
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100)
    missing_pct = missing_pct[missing_pct > 0]
    
    if len(missing_pct) > 0:
        ax.barh(missing_pct.index, missing_pct.values, color='#e74c3c', alpha=0.7)
        ax.set_xlabel('Percentage Missing (%)')
        ax.set_title('Missing Values by Column', fontsize=14, fontweight='bold')
    else:
        ax.text(0.5, 0.5, 'No Missing Values', ha='center', va='center', 
                fontsize=16, transform=ax.transAxes)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(FIGURES / "03_missing_values.png", dpi=150)
    plt.close()
    print("   📊 Chart 3/5: 03_missing_values.png")

def plot_amount_distribution(df):
    """Chart 4: Amount distribution"""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(df['amount'], bins=30, color='#3498db', alpha=0.7, edgecolor='black')
    ax.set_xlabel('Amount')
    ax.set_ylabel('Frequency')
    ax.set_title('Transaction Amount Distribution', fontsize=14, fontweight='bold')
    ax.axvline(df['amount'].mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: ${df["amount"].mean():.2f}')
    ax.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / "04_amount_distribution.png", dpi=150)
    plt.close()
    print("   📊 Chart 4/5: 04_amount_distribution.png")

def plot_temporal_trends(df):
    """Chart 5: Temporal trends"""
    fig, ax = plt.subplots(figsize=(10, 6))
    if 'timestamp' in df.columns:
        df_temp = df.copy()
        df_temp['timestamp'] = pd.to_datetime(df_temp['timestamp'])
        df_temp = df_temp.sort_values('timestamp')
        df_temp['date'] = df_temp['timestamp'].dt.date
        daily_amounts = df_temp.groupby('date')['amount'].sum()
        ax.plot(daily_amounts.index, daily_amounts.values, marker='o', linewidth=2, 
                markersize=6, color='#9b59b6')
        ax.set_xlabel('Date')
        ax.set_ylabel('Daily Transaction Amount ($)')
        ax.set_title('Daily Transaction Amount Over Time', fontsize=14, fontweight='bold')
    else:
        ax.text(0.5, 0.5, 'No timestamp data available', ha='center', va='center', 
                fontsize=14, transform=ax.transAxes)
        ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(FIGURES / "05_temporal_trends.png", dpi=150)
    plt.close()
    print("   📊 Chart 5/5: 05_temporal_trends.png")

def main():
    print("   Task 2B — EDA Report")
    
    # Load clean data
    df = pd.read_parquet(DATA_PROCESSED / "clean.parquet")
    
    print(f"   📊 Generating 5 EDA charts...\n")
    plot_target_distribution(df)
    plot_feature_correlations(df)
    plot_missing_values(df)
    plot_amount_distribution(df)
    plot_temporal_trends(df)
    
    print(f"\n   ✅ 5 EDA charts saved to reports/figures/")

if __name__ == "__main__":
    main()
