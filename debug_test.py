#!/usr/bin/env python3
"""
Debug test - minimal script to find the issue
"""
import sys
import os

print("START", flush=True)

# Test 1: Check if we can import
print("Test 1: Importing libraries...", flush=True)
try:
    import pandas as pd
    print("  ✓ pandas imported", flush=True)
except Exception as e:
    print(f"  ✗ pandas failed: {e}", flush=True)
    sys.exit(1)

try:
    import numpy as np
    print("  ✓ numpy imported", flush=True)
except Exception as e:
    print(f"  ✗ numpy failed: {e}", flush=True)
    sys.exit(1)

try:
    from sklearn.ensemble import RandomForestClassifier
    print("  ✓ sklearn imported", flush=True)
except Exception as e:
    print(f"  ✗ sklearn failed: {e}", flush=True)
    sys.exit(1)

# Test 2: Find dataset
print("\nTest 2: Finding dataset...", flush=True)
possible_paths = ["Dataset.csv", "icu-early-warning/Dataset.csv", "../Dataset.csv"]
dataset_path = None

for path in possible_paths:
    print(f"  Checking {path}...", flush=True)
    if os.path.exists(path):
        dataset_path = path
        print(f"  ✓ Found at {path}", flush=True)
        break

if dataset_path is None:
    print("  ✗ Dataset not found!", flush=True)
    print("  Available files:", flush=True)
    for f in os.listdir("."):
        print(f"    - {f}", flush=True)
    sys.exit(1)

# Test 3: Load dataset
print("\nTest 3: Loading dataset...", flush=True)
try:
    df = pd.read_csv(dataset_path)
    print(f"  ✓ Loaded {len(df)} rows, {len(df.columns)} columns", flush=True)
except Exception as e:
    print(f"  ✗ Failed to load: {e}", flush=True)
    sys.exit(1)

# Test 4: Find target
print("\nTest 4: Finding target column...", flush=True)
target_col = None
for col in df.columns:
    if 'sepsis' in col.lower() or 'target' in col.lower() or 'label' in col.lower():
        target_col = col
        print(f"  ✓ Found target: {target_col}", flush=True)
        break

if target_col is None:
    print("  ✗ Target not found!", flush=True)
    print("  Columns:", flush=True)
    for col in df.columns:
        print(f"    - {col}", flush=True)
    sys.exit(1)

# Test 5: Basic stats
print("\nTest 5: Data statistics...", flush=True)
print(f"  Shape: {df.shape}", flush=True)
print(f"  Target distribution: {df[target_col].value_counts().to_dict()}", flush=True)
print(f"  Missing values: {df.isnull().sum().sum()}", flush=True)

print("\n✅ ALL TESTS PASSED", flush=True)
print("Dataset is ready for model training", flush=True)
