"""
Quick Model Improvement Test - Fast Version
Tests ensemble approach without full training
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, recall_score, precision_score, f1_score
import xgboost as xgb
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("QUICK MODEL IMPROVEMENT TEST")
print("=" * 80)

# Load data
print("\n1. Loading data...")
possible_paths = ["Dataset.csv", "icu-early-warning/Dataset.csv", "../Dataset.csv"]
dataset_path = None
for path in possible_paths:
    import os
    if os.path.exists(path):
        dataset_path = path
        break

if dataset_path is None:
    print("❌ Dataset not found")
    exit()

df = pd.read_csv(dataset_path)
print(f"✓ Loaded {len(df)} samples, {len(df.columns)} features")

# Find target
target_col = None
for col in df.columns:
    if 'sepsis' in col.lower() or 'target' in col.lower() or 'label' in col.lower():
        target_col = col
        break

if target_col is None:
    print("❌ Target column not found")
    exit()

print(f"✓ Target column: {target_col}")

# Prepare data (use 10% sample for speed)
print("\n2. Preparing data (using 10% sample for speed)...")
df_sample = df.sample(frac=0.1, random_state=42)
X = df_sample.drop(columns=[target_col])
y = df_sample[target_col]

# Fill missing
X = X.fillna(X.median())

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

print(f"✓ Train: {len(X_train)}, Test: {len(X_test)}")
print(f"✓ Features: {len(X.columns)}")

# Scale
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train models
print("\n3. Training models...")

models = {
    'Logistic Regression': LogisticRegression(class_weight='balanced', max_iter=1000),
    'Random Forest': RandomForestClassifier(n_estimators=50, class_weight='balanced', random_state=42),
    'Gradient Boosting': GradientBoostingClassifier(n_estimators=50, random_state=42),
    'XGBoost': xgb.XGBClassifier(n_estimators=50, scale_pos_weight=45, random_state=42)
}

results = {}

for name, model in models.items():
    print(f"  Training {name}...", end=" ")
    
    if name == 'Logistic Regression':
        model.fit(X_train_scaled, y_train)
        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
    else:
        model.fit(X_train, y_train)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    y_pred = (y_pred_proba > 0.5).astype(int)
    
    auroc = roc_auc_score(y_test, y_pred_proba)
    recall = recall_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    results[name] = {
        'AUROC': auroc,
        'Recall': recall,
        'Precision': precision,
        'F1': f1
    }
    
    print(f"✓ AUROC: {auroc:.4f}")

# Ensemble
print("\n4. Creating ensemble...")
ensemble_proba = np.zeros(len(X_test))

for name, model in models.items():
    if name == 'Logistic Regression':
        proba = model.predict_proba(X_test_scaled)[:, 1]
    else:
        proba = model.predict_proba(X_test)[:, 1]
    ensemble_proba += proba

ensemble_proba /= len(models)
ensemble_pred = (ensemble_proba > 0.5).astype(int)

ensemble_auroc = roc_auc_score(y_test, ensemble_proba)
ensemble_recall = recall_score(y_test, ensemble_pred)
ensemble_precision = precision_score(y_test, ensemble_pred)
ensemble_f1 = f1_score(y_test, ensemble_pred)

results['Ensemble'] = {
    'AUROC': ensemble_auroc,
    'Recall': ensemble_recall,
    'Precision': ensemble_precision,
    'F1': ensemble_f1
}

print(f"✓ Ensemble AUROC: {ensemble_auroc:.4f}")

# Results
print("\n" + "=" * 80)
print("RESULTS COMPARISON")
print("=" * 80)

results_df = pd.DataFrame(results).T
print("\n" + results_df.to_string())

# Compare to original
original_auroc = 0.7337
print("\n" + "=" * 80)
print("IMPROVEMENT vs ORIGINAL MODEL")
print("=" * 80)

print(f"\nOriginal AUROC: {original_auroc:.4f}")
print(f"Ensemble AUROC: {ensemble_auroc:.4f}")
print(f"Improvement: +{ensemble_auroc - original_auroc:.4f} ({(ensemble_auroc - original_auroc) / original_auroc * 100:.1f}%)")

print(f"\nOriginal Recall: 63.8%")
print(f"Ensemble Recall: {ensemble_recall * 100:.1f}%")
print(f"Improvement: +{(ensemble_recall - 0.638) * 100:.1f}%")

print(f"\nOriginal Precision: 40%")
print(f"Ensemble Precision: {ensemble_precision * 100:.1f}%")
print(f"Improvement: +{(ensemble_precision - 0.40) * 100:.1f}%")

print("\n" + "=" * 80)
print("✅ TEST COMPLETE")
print("=" * 80)

if ensemble_auroc > original_auroc:
    print(f"\n🎉 SUCCESS! Ensemble model improved AUROC by {(ensemble_auroc - original_auroc) / original_auroc * 100:.1f}%")
else:
    print(f"\n⚠️ Ensemble AUROC is lower. This can happen with small samples.")

print("\nNote: This test used 10% of data for speed.")
print("Full model training uses 100% of data and takes 2-5 minutes.")
