# ICU Early Warning Agent - Quick Start Guide

## Environment Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Running the Modules

### 1. Data Ingestion & Validation
```bash
venv/bin/python src/data_ingestion_v2.py
```
**Output**: Dataset overview, missing values analysis, class distribution

### 2. Clinical Feature Engineering
```bash
venv/bin/python src/feature_engineering.py
```
**Output**: 51 new clinical features including:
- Shock Index (HR/SBP)
- Pulse Pressure (SBP - DBP)
- Instability flags (high HR, low SBP, low MAP)
- Missingness indicators

### 3. Imbalance-Aware Model Training
```bash
venv/bin/python src/model_training.py
```
**Output**: 
- Baseline Logistic Regression (no class weighting)
- Weighted Logistic Regression (class_weight='balanced')
- Comparison metrics: AUROC, PR-AUC, Precision, Recall, F1

### 4. Model Calibration & Threshold Optimization
```bash
venv/bin/python src/calibration_and_thresholds.py
```
**Output**:
- Calibration evaluation (Brier score, overconfidence analysis)
- Probability calibration (isotonic regression)
- Threshold optimization (sensitivity, precision, F1 at each threshold)
- Clinical threshold recommendations (high-sensitivity & balanced)
- Calibration curve and threshold performance plots

### 5. Clinical Interpretability & Explainability
```bash
venv/bin/python src/explanation.py
```
**Output**:
- Global feature importance (top 15 features ranked)
- Local patient explanations (why specific predictions were made)
- Clinical narratives (clinician-friendly reports)
- Feature importance and patient contribution plots

### 6. Streamlit Dashboard
```bash
streamlit run app.py
```
**Output**: Interactive web dashboard showing:
- Dataset overview
- Class distribution
- Missing values analysis
- Data quality metrics

## Key Files

| File | Purpose |
|------|---------|
| `src/data_ingestion_v2.py` | Load, validate, and analyze dataset |
| `src/feature_engineering.py` | Create clinical features |
| `src/model_training.py` | Train and evaluate models |
| `src/calibration_and_thresholds.py` | Calibrate probabilities and optimize thresholds |
| `src/explanation.py` | Clinical interpretability and explainability |
| `app.py` | Streamlit dashboard |
| `Dataset.csv` | Input data (546K rows × 44 columns) |
| `CALIBRATION_GUIDE.md` | Detailed calibration and threshold guide |
| `EXPLAINABILITY_GUIDE.md` | Clinical interpretability guide |

## Dataset Info

- **Size**: 546,123 patient-hours × 44 features
- **Target**: SepsisLabel (binary: 0=no sepsis, 1=sepsis)
- **Class Imbalance**: 97.83% negative, 2.17% positive (45:1 ratio)
- **Missing Data**: Highly sparse (many features >85% missing)

## Key Metrics

### Baseline Model (No Class Weighting)
- AUROC: 0.7264
- Recall: 0.0% (misses all sepsis cases)
- Precision: 0.0%

### Weighted Model (Balanced Classes)
- AUROC: 0.7337
- Recall: 63.8% (catches 64% of sepsis cases)
- Precision: 5.1%
- **Better for early warning**: Prioritizes catching sepsis over false alarms

## Why Weighted Model?

For an early warning system, **recall is critical**:
- Missing sepsis cases (false negatives) = clinical risk
- False alarms (false positives) = acceptable cost
- Weighted model achieves 63.8% recall vs 0% baseline

## Next Steps

1. ✅ Data Ingestion - Complete
2. ✅ Feature Engineering - Complete
3. ✅ Model Training - Complete
4. ✅ Model Calibration & Thresholds - Complete
5. ✅ Clinical Interpretability - Complete
6. 📊 Dashboard Integration - In progress
7. ⏱️ Simulator Module - Planned

## Troubleshooting

**"Dataset.csv not found"**
- Ensure Dataset.csv is in the `icu-early-warning/` folder
- Check file path in scripts

**"ModuleNotFoundError: No module named 'pandas'"**
- Activate venv: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

**Streamlit not found**
- Install: `pip install streamlit`
- Run from project root: `streamlit run icu-early-warning/app.py`

**Slow execution**
- Scripts sample 5% of data for faster training
- Full dataset training takes longer
- Adjust `frac=0.05` in model_training.py to change sample size
