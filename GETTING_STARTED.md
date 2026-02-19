# Getting Started: ICU Early Warning Agent

## Quick Start

### 1. Setup Environment
```bash
cd icu-early-warning
bash setup.sh
source venv/bin/activate
```

### 2. Download Data
1. Visit: https://physionet.org/content/challenge-2019/
2. Download the training dataset
3. Extract to `data/training_data/`
4. Verify you have:
   - `data/training_data/p000001.psv`
   - `data/training_data/p000002.psv`
   - ... (many more patient files)
   - `data/training_data/sepsis_labels.csv`

### 3. Run Data Ingestion
```bash
python src/data_ingestion.py
```

This will:
- Load all patient files
- Validate schema
- Align labels
- Create processed dataset

### 4. Run Feature Engineering
```bash
python src/feature_engineering.py
```

This will:
- Create patient-hour rows
- Compute rolling statistics
- Add missingness flags
- Create lookahead labels
- Output: `data/processed/patient_hours.csv`

### 5. Train Baseline Model
```bash
python src/baseline_model.py
```

This will:
- Split data (80/10/10 by patient)
- Apply SMOTE to training set
- Train logistic regression
- Save model artifacts

### 6. Evaluate Model
```bash
python src/evaluation.py
```

This will:
- Compute all metrics (AUROC, AUPRC, etc.)
- Generate plots (ROC, PR, calibration curves)
- Output: `results/baseline_results.json`

### 7. Generate Explanations
```bash
python src/explanation.py
```

This will:
- Compute feature importance
- Generate per-prediction explanations
- Output: `results/feature_importance.csv`

### 8. Simulate Patient Timeline
```bash
python src/simulator.py --patient_id p000042
```

This will:
- Replay patient hour-by-hour
- Show risk scores and alerts
- Generate timeline visualization
- Output: `results/patient_p000042_timeline.png`

---

## Project Structure

```
icu-early-warning/
├── README.md                    # Project overview
├── SPEC.md                      # Detailed specification
├── EVALUATION_PLAN.md           # Research evaluation protocol
├── DATA_SCHEMA.md               # Data format & mapping
├── PROJECT_PLAN.md              # Milestones & timeline
├── GETTING_STARTED.md           # This file
├── requirements.txt             # Python dependencies
├── setup.sh                     # Environment setup
├── data/
│   ├── training_data/           # Raw PhysioNet dataset (user-provided)
│   │   ├── p000001.psv
│   │   ├── p000002.psv
│   │   └── sepsis_labels.csv
│   └── processed/               # Engineered dataset
│       ├── patient_hours.csv
│       ├── train_indices.pkl
│       ├── val_indices.pkl
│       └── test_indices.pkl
├── src/
│   ├── __init__.py
│   ├── data_ingestion.py        # Load & validate data
│   ├── feature_engineering.py   # Time-series features
│   ├── baseline_model.py        # Logistic regression
│   ├── evaluation.py            # Metrics & evaluation
│   ├── explanation.py           # Feature importance
│   └── simulator.py             # Patient timeline replay
├── models/                      # Saved model artifacts
│   ├── baseline_model.pkl
│   ├── scaler.pkl
│   └── feature_names.pkl
├── results/                     # Results & visualizations
│   ├── baseline_results.json
│   ├── feature_importance.csv
│   ├── roc_curve.png
│   ├── pr_curve.png
│   └── patient_timelines/
└── notebooks/
    └── exploration.ipynb        # EDA & prototyping
```

---

## Key Files to Review

1. **SPEC.md** - Detailed specification of the prediction task, features, and modules
2. **EVALUATION_PLAN.md** - Research-grade evaluation protocol with all metrics
3. **DATA_SCHEMA.md** - Exact data format and how raw data maps to patient-hour rows
4. **PROJECT_PLAN.md** - 4-week implementation roadmap with milestones

---

## Module Overview

### Data Ingestion (`src/data_ingestion.py`)
- Loads patient .psv files from PhysioNet
- Validates schema (required columns)
- Aligns sepsis labels with vital signs
- Handles missing values

### Feature Engineering (`src/feature_engineering.py`)
- Converts time-series to patient-hour rows
- Computes rolling statistics (6h, 12h windows)
- Adds missingness indicators
- Creates lookahead labels (6-hour prediction horizon)

### Baseline Model (`src/baseline_model.py`)
- Logistic regression classifier
- Handles class imbalance (SMOTE on training set)
- Provides feature importance (coefficients)
- Predicts risk scores [0, 1]

### Evaluation (`src/evaluation.py`)
- AUROC (Area Under ROC Curve)
- AUPRC (Area Under Precision-Recall Curve)
- Sensitivity at fixed FPR
- Median hours early (true positives only)
- Calibration metrics (Brier score)

### Explanation (`src/explanation.py`)
- Global feature importance
- Per-prediction explanations
- SHAP values (optional)
- Natural language summaries

### Simulator (`src/simulator.py`)
- Replays patient timeline hour-by-hour
- Shows risk scores and alerts
- Visualizes timeline with sepsis onset marker
- Generates clinical reports

---

## Expected Results (Baseline)

| Metric | Expected | Target |
|--------|----------|--------|
| AUROC | 0.75-0.80 | ≥0.80 |
| AUPRC | 0.50-0.60 | ≥0.60 |
| Sensitivity@FPR=0.10 | 0.60-0.70 | ≥0.70 |
| Median Hours Early | 2-3 hours | ≥3 hours |
| Brier Score | 0.12-0.15 | <0.15 |

---

## Troubleshooting

### Issue: "No such file or directory: data/training_data/p000001.psv"
**Solution**: Download PhysioNet dataset and extract to `data/training_data/`

### Issue: "Missing required columns"
**Solution**: Verify dataset format matches DATA_SCHEMA.md

### Issue: "Class imbalance too severe"
**Solution**: Adjust SMOTE ratio or use class weights in model

### Issue: "Model overfitting"
**Solution**: Use cross-validation, reduce features, increase regularization

---

## Next Steps

1. ✓ Review SPEC.md for detailed requirements
2. ✓ Review EVALUATION_PLAN.md for metrics
3. ✓ Review DATA_SCHEMA.md for data format
4. ✓ Download PhysioNet dataset
5. → Run data ingestion & feature engineering
6. → Train baseline model
7. → Evaluate and iterate

---

## Questions?

Refer to:
- **SPEC.md** for what to build
- **EVALUATION_PLAN.md** for how to evaluate
- **DATA_SCHEMA.md** for data format
- **PROJECT_PLAN.md** for timeline & milestones

Good luck! 🚀
