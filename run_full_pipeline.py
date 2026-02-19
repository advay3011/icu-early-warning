#!/usr/bin/env python3
"""
Complete pipeline runner - Enrichment + Improved Model + Dashboard prep
Runs with minimal data sample for quick testing
"""

import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=" * 80)
print("ICU EARLY WARNING SYSTEM - FULL PIPELINE")
print("=" * 80)

# Step 1: Load dataset
print("\n[STEP 1] Loading dataset...")
try:
    df = pd.read_csv('icu-early-warning/Dataset.csv')
    print(f"✓ Loaded {len(df)} rows × {len(df.columns)} columns")
except FileNotFoundError:
    try:
        df = pd.read_csv('Dataset.csv')
        print(f"✓ Loaded {len(df)} rows × {len(df.columns)} columns")
    except FileNotFoundError:
        print("❌ Dataset.csv not found")
        sys.exit(1)

# Use 5% sample for quick testing
print("\n[STEP 2] Sampling data (5% for quick testing)...")
df_sample = df.sample(frac=0.05, random_state=42)
print(f"✓ Working with {len(df_sample)} rows")

# Step 3: Enrich dataset
print("\n[STEP 3] Enriching dataset with realistic features...")
print("  Adding demographics...")
df_sample['age'] = np.random.normal(loc=65, scale=15, size=len(df_sample)).clip(18, 95)
df_sample['gender'] = np.random.choice(['Male', 'Female'], size=len(df_sample))
df_sample['bmi'] = np.random.normal(loc=28, scale=6, size=len(df_sample)).clip(15, 50)

print("  Adding comorbidities...")
comorbidities = {
    'diabetes': 0.30, 'hypertension': 0.40, 'heart_disease': 0.25,
    'kidney_disease': 0.15, 'liver_disease': 0.10, 'immunosuppressed': 0.20,
}
for condition, prev in comorbidities.items():
    df_sample[condition] = np.random.binomial(1, prev, size=len(df_sample))
df_sample['comorbidity_score'] = df_sample[[col for col in comorbidities.keys()]].sum(axis=1)

print("  Adding infection source...")
df_sample['infection_source'] = np.random.choice(
    ['respiratory', 'urinary', 'abdominal', 'bloodstream', 'other'],
    size=len(df_sample), p=[0.40, 0.30, 0.15, 0.10, 0.05]
)

print("  Adding medications...")
medications = {
    'on_antibiotics': 0.70, 'on_vasopressors': 0.30, 'on_sedatives': 0.60,
    'on_anticoagulation': 0.40, 'on_steroids': 0.25, 'on_insulin': 0.50,
}
for med, prev in medications.items():
    df_sample[med] = np.random.binomial(1, prev, size=len(df_sample))
df_sample['medication_intensity'] = df_sample[[col for col in medications.keys()]].sum(axis=1)

print(f"✓ Enrichment complete: {len(df_sample.columns)} total features")

# Step 4: Train improved model
print("\n[STEP 4] Training improved ensemble model...")
try:
    from improved_model import ImprovedModelTrainer
    
    # Identify target column
    target_col = 'SepsisLabel' if 'SepsisLabel' in df_sample.columns else None
    if target_col is None:
        print("❌ SepsisLabel column not found")
        sys.exit(1)
    
    trainer = ImprovedModelTrainer(df_sample, target_col=target_col)
    print("✓ Model trainer initialized")
    
    print("  Training ensemble models...")
    trainer.train_ensemble()
    print("✓ Ensemble training complete")
    
    print("  Evaluating models...")
    trainer.evaluate_ensemble()
    print("✓ Evaluation complete")
    
    print("\n" + "=" * 80)
    print("MODEL PERFORMANCE SUMMARY")
    print("=" * 80)
    trainer.print_summary()
    
except Exception as e:
    print(f"⚠️  Model training error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("PIPELINE COMPLETE")
print("=" * 80)
print("\nNext steps:")
print("1. Run: streamlit run clinical_dashboard.py")
print("2. Open: http://localhost:8504")
print("3. Test the dashboard with sample patient data")
