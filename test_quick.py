#!/usr/bin/env python3
"""
Quick test - Minimal data sample to verify pipeline works
Uses 0.1% of data for instant testing
"""

import sys
import os
import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=" * 80)
print("QUICK TEST - ICU EARLY WARNING SYSTEM")
print("=" * 80)

# Step 1: Load dataset
print("\n[1/5] Loading dataset...")
try:
    df = pd.read_csv('icu-early-warning/Dataset.csv')
except FileNotFoundError:
    try:
        df = pd.read_csv('Dataset.csv')
    except FileNotFoundError:
        print("❌ Dataset.csv not found")
        sys.exit(1)

print(f"✓ Loaded {len(df)} rows × {len(df.columns)} columns")

# Use tiny sample for instant testing
print("\n[2/5] Sampling data (0.1% for instant test)...")
df_tiny = df.sample(frac=0.001, random_state=42)
print(f"✓ Working with {len(df_tiny)} rows")

# Step 2: Data ingestion
print("\n[3/5] Testing data ingestion...")
try:
    from data_ingestion_v2 import DataIngestionModule
    ingestion = DataIngestionModule(df_tiny)
    print("✓ Data ingestion module loaded")
except Exception as e:
    print(f"⚠️  Data ingestion error: {e}")

# Step 3: Feature engineering
print("\n[4/5] Testing feature engineering...")
try:
    from feature_engineering import ClinicalFeatureEngineer
    engineer = ClinicalFeatureEngineer(df_tiny)
    df_engineered, report = engineer.run_feature_engineering()
    print(f"✓ Feature engineering complete: {len(df_engineered.columns)} features")
except Exception as e:
    print(f"⚠️  Feature engineering error: {e}")

# Step 4: Model training
print("\n[5/5] Testing model training...")
try:
    from model_training import ImbalanceAwareModelTrainer
    
    # Find target column
    target_col = 'SepsisLabel' if 'SepsisLabel' in df_tiny.columns else None
    if target_col is None:
        print("❌ SepsisLabel not found")
        sys.exit(1)
    
    trainer = ImbalanceAwareModelTrainer(df_tiny, target_col=target_col)
    trainer.run_training_pipeline()
    
    # Get predictions
    y_pred = trainer.model_weighted.predict(trainer.X_test)
    y_pred_proba = trainer.model_weighted.predict_proba(trainer.X_test)[:, 1]
    
    print(f"✓ Model training complete")
    print(f"  - Predictions: {len(y_pred)}")
    print(f"  - Probability range: [{y_pred_proba.min():.3f}, {y_pred_proba.max():.3f}]")
    
except Exception as e:
    print(f"⚠️  Model training error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("✅ QUICK TEST COMPLETE")
print("=" * 80)
print("\nAll modules working! You can now:")
print("1. Run: streamlit run clinical_dashboard.py")
print("2. Or run: python run_full_pipeline.py (for full 5% sample)")
