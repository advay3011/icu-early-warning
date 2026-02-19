"""Quick model training test - minimal version"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score

print("Loading data...")
df = pd.read_csv("icu-early-warning/Dataset.csv")
print(f"✓ Loaded {df.shape[0]} rows × {df.shape[1]} columns")

# Sample for speed
print("Sampling 2% for quick test...")
df = df.sample(frac=0.02, random_state=42)
print(f"✓ Sampled: {df.shape}")

# Find target
target_col = 'SepsisLabel'
X = df.drop(columns=[target_col])
y = df[target_col]

# Remove NaN targets
valid_idx = y.notna()
X = X[valid_idx]
y = y[valid_idx]

# Drop all-NaN columns
X = X.dropna(axis=1, how='all')

print(f"\nDataset: {X.shape}")
print(f"Target distribution: {y.value_counts().to_dict()}")

# Split
print("\nSplitting data...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# Impute
print("Imputing missing values...")
imputer = SimpleImputer(strategy='median')
X_train = pd.DataFrame(imputer.fit_transform(X_train), columns=X_train.columns)
X_test = pd.DataFrame(imputer.transform(X_test), columns=X_test.columns)

# Train baseline
print("\nTraining baseline model...")
model_baseline = LogisticRegression(max_iter=1000, random_state=42)
model_baseline.fit(X_train, y_train)

# Train weighted
print("Training weighted model...")
model_weighted = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42)
model_weighted.fit(X_train, y_train)

# Evaluate
print("\n" + "="*80)
print("MODEL EVALUATION")
print("="*80)

for name, model in [("Baseline", model_baseline), ("Weighted", model_weighted)]:
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    print(f"\n{name} Model:")
    print(f"  AUROC: {roc_auc_score(y_test, y_pred_proba):.4f}")
    print(f"  Precision: {precision_score(y_test, y_pred):.4f}")
    print(f"  Recall: {recall_score(y_test, y_pred):.4f}")
    print(f"  F1: {f1_score(y_test, y_pred):.4f}")

print("\n✓ Model training complete!")
