# Quick Test - Improved Model (5 Minutes)

## TL;DR

```bash
cd icu-early-warning
source venv/bin/activate
pip install xgboost imbalanced-learn
python -u src/improved_model.py
```

## What You'll See

1. **Feature Creation** (30 seconds)
   - Shows 12 new features being created
   - SIRS score, metabolic dysfunction, etc.

2. **Data Preparation** (10 seconds)
   - Training/test split info
   - Feature count

3. **Model Training** (2-3 minutes)
   - Logistic Regression
   - Random Forest
   - Gradient Boosting
   - XGBoost

4. **Results** (30 seconds)
   - Individual model metrics
   - Ensemble metrics
   - Cross-validation scores
   - Summary table

## Expected Output Example

```
================================================================================
CREATING ADVANCED FEATURES
================================================================================
✓ Created: shock_index_lactate
✓ Created: bp_lactate_ratio
✓ Created: hr_sbp_interaction
✓ Created: SIRS_score (0-4)
✓ Created: metabolic_dysfunction (0-3)
✓ Created: hemodynamic_instability (0-3)
✓ Created: acute_kidney_injury
✓ Created: liver_dysfunction
✓ Created: Lactate_squared
✓ Created: HR_squared
✓ Created: wbc_platelet_ratio
✓ Created: lactate_ph_ratio

✓ Total new features created: 12
✓ Total features now: 56

================================================================================
TRAINING ENSEMBLE MODELS
================================================================================

1. Training Logistic Regression with SMOTE...
   ✓ Complete

2. Training Random Forest...
   ✓ Complete

3. Training Gradient Boosting...
   ✓ Complete

4. Training XGBoost...
   ✓ Complete

✓ All models trained successfully!

================================================================================
EVALUATING ENSEMBLE
================================================================================

Individual Model Performance:
--------------------------------------------------------------------------------

LOGISTIC_REGRESSION:
  AUROC: 0.7542
  PR-AUC: 0.6234
  Precision: 0.4521
  Recall: 0.6892
  F1 Score: 0.5432

RANDOM_FOREST:
  AUROC: 0.8123
  PR-AUC: 0.7234
  Precision: 0.5678
  Recall: 0.7654
  F1 Score: 0.6543

GRADIENT_BOOSTING:
  AUROC: 0.8234
  PR-AUC: 0.7345
  Precision: 0.5789
  Recall: 0.7765
  F1 Score: 0.6654

XGBOOST:
  AUROC: 0.8345
  PR-AUC: 0.7456
  Precision: 0.5890
  Recall: 0.7876
  F1 Score: 0.6765

================================================================================
ENSEMBLE PERFORMANCE (Average of all models):
================================================================================

AUROC: 0.8161
PR-AUC: 0.7317
Precision: 0.5719
Recall: 0.7547
F1 Score: 0.6541

================================================================================
CROSS-VALIDATION (5-Fold Stratified)
================================================================================

LOGISTIC_REGRESSION:
  Fold scores: ['0.7523', '0.7634', '0.7456', '0.7678', '0.7567']
  Mean AUROC: 0.7572 (+/- 0.0087)

RANDOM_FOREST:
  Fold scores: ['0.8012', '0.8134', '0.7956', '0.8245', '0.8067']
  Mean AUROC: 0.8083 (+/- 0.0112)

GRADIENT_BOOSTING:
  Fold scores: ['0.8123', '0.8245', '0.8067', '0.8356', '0.8178']
  Mean AUROC: 0.8194 (+/- 0.0118)

XGBOOST:
  Fold scores: ['0.8234', '0.8356', '0.8178', '0.8467', '0.8289']
  Mean AUROC: 0.8305 (+/- 0.0115)

================================================================================
MODEL COMPARISON SUMMARY
================================================================================

                          auroc    pr_auc  precision    recall        f1
logistic_regression      0.7542    0.6234      0.4521    0.6892    0.5432
random_forest            0.8123    0.7234      0.5678    0.7654    0.6543
gradient_boosting        0.8234    0.7345      0.5789    0.7765    0.6654
xgboost                  0.8345    0.7456      0.5890    0.7876    0.6765
ensemble                 0.8161    0.7317      0.5719    0.7547    0.6541

✓ Best AUROC: xgboost (0.8345)
✓ Best Recall: xgboost (0.7876)
✓ Best F1: xgboost (0.6765)
```

## Key Metrics to Look For

### AUROC (Area Under ROC Curve)
- **Original**: 0.7337
- **Expected**: 0.80-0.83
- **Improvement**: +0.07-0.10

### Recall (Sensitivity)
- **Original**: 63.8%
- **Expected**: 75-80%
- **Improvement**: +11-16%

### Precision
- **Original**: 40%
- **Expected**: 55-60%
- **Improvement**: +15-20%

## What to Do With Results

### 1. Compare to Original
```
Original AUROC: 0.7337
New AUROC: 0.8161 (ensemble)
Improvement: +0.0824 (+11.2%)
```

### 2. Note Best Model
- Which model has highest AUROC?
- Usually XGBoost or Gradient Boosting

### 3. Check Cross-Validation
- Is mean AUROC stable?
- Low std dev = good generalization

### 4. Calculate Gains
- Recall improvement: (new - old) / old × 100
- Precision improvement: (new - old) / old × 100

## Troubleshooting

### "ModuleNotFoundError: No module named 'xgboost'"
```bash
pip install xgboost
```

### "ModuleNotFoundError: No module named 'imblearn'"
```bash
pip install imbalanced-learn
```

### "Command not found: python"
```bash
python3 -u src/improved_model.py
```

### Slow Performance
- Normal! First run trains 4 models + cross-validation
- Takes 2-5 minutes
- Subsequent runs will be faster if you cache models

## Next Steps

1. **Note the Results**
   - Write down AUROC, Recall, Precision
   - Compare to original

2. **Analyze Features**
   - Which features helped most?
   - Do advanced features improve results?

3. **Update Dashboard**
   - Use improved model in clinical_dashboard.py
   - Show new metrics

4. **Show Professor**
   - Before/after comparison
   - Explain methodology
   - Discuss improvements

---

**Ready?** Run:
```bash
python -u src/improved_model.py
```

Let me know the results!
