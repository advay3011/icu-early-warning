# ICU Sepsis Early Warning System

A machine learning model for early sepsis detection in ICU patients using clinical vital signs and laboratory values.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Research Grade](https://img.shields.io/badge/Status-Research%20Grade-blue.svg)]()

## Problem

Sepsis is a leading cause of ICU mortality. Early detection is critical—every hour of delay increases mortality risk. This project develops a machine learning model to identify high-risk patients from readily available vital signs and laboratory values.

## Dataset

**Source**: PhysioNet ICU Challenge 2019  
**Size**: 546,123 patient-hours (~40,000 unique ICU admissions)  
**Class Distribution**: 97.8% no sepsis / 2.2% sepsis (realistic ICU imbalance)  
**Features**: 44 raw clinical variables → 51 engineered clinical features

## Model

**Algorithm**: Weighted Logistic Regression with isotonic calibration  
**Validation**: 5-fold stratified cross-validation  
**Training Data**: 546K patient-hours with class weighting for imbalance

### Performance

| Metric | Value |
|--------|-------|
| **AUROC** | 0.7337 |
| **Recall** | 63.8% |
| **Precision** | 5.1% |
| **Specificity** | 99.2% |
| **Brier Score** | 0.0195 |

**Interpretation**: The model catches ~64% of sepsis cases with a 5.1% positive predictive value. This reflects a deliberate clinical choice to prioritize sensitivity (catching cases) over precision (reducing false alarms). At the recommended threshold (0.25), sensitivity is 78.4% and specificity is 96.1%.

## Features

**Hemodynamic** (8): Shock Index, MAP, Pulse Pressure, HR, BP variants  
**Inflammatory** (6): SIRS Score, WBC, Temperature, Lactate  
**Organ Dysfunction** (12): SOFA components, Creatinine, Bilirubin, Platelets, INR  
**Metabolic** (10): O2 Sat, pH, Glucose, Electrolytes, Base Excess  
**Risk Scores** (7): qSOFA, SIRS, SOFA, Shock Index variants  
**Demographics** (2): Age, Gender

## Quick Start

```bash
# Clone and setup
git clone https://github.com/advay3011/icu-early-warning.git
cd icu-early-warning

# Create environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Launch dashboard
streamlit run clinical_dashboard.py --server.port 8506
```

Open: **http://localhost:8506**

## Project Structure

```
icu-early-warning/
├── clinical_dashboard.py          # User-friendly Streamlit dashboard
├── src/
│   ├── data_ingestion_v2.py       # Data loading & validation
│   ├── feature_engineering.py     # 51 clinical features
│   ├── model_training.py          # Model training & evaluation
│   ├── calibration_and_thresholds.py # Probability calibration
│   ├── explanation.py             # SHAP explainability
│   └── simulator.py               # Clinical simulation
├── research_grade/                # Research-grade implementation
│   ├── config.py                  # Clinical features & reference ranges
│   ├── model.py                   # Rigorous validation (ROC, calibration curves)
│   ├── ui.py                      # Advanced dashboard (6 tabs)
│   └── utils.py                   # Clinical calculations
├── Dataset.csv                    # Input data (546K patient-hours)
└── requirements.txt               # Dependencies
```

## Usage

```python
# Patient vitals
patient = {
    'HR': 110, 'SBP': 95, 'DBP': 60, 'O2Sat': 92,
    'Temp': 38.5, 'Resp': 22, 'WBC': 14.2, 'Lactate': 3.2,
    'gender': 'Male'
}

# Model predicts
Risk: 72% (HIGH)
Top factors: High lactate, Low BP, Elevated HR
```

## Important Limitations

- **Not FDA Approved**: Research tool only
- **Lower Precision**: 5.1% PPV means ~19 false alerts per true positive
- **Batch Processing**: Not real-time streaming
- **Requires Validation**: Needs clinical validation before hospital deployment
- **Imbalanced Data**: Trained on 97.8% negative class; generalization to different prevalence unknown
- **Single Time Point**: Snapshot prediction; doesn't use temporal trends

## Documentation

- **[MODEL_CARD.md](MODEL_CARD.md)** - Comprehensive model documentation
- **[research_grade/README.md](research_grade/README.md)** - Technical details & validation
- **[src/](src/)** - Implementation details

## Ethical Considerations

- **Fairness**: No stratified analysis by gender/age; potential bias unknown
- **Transparency**: SHAP values provided for each prediction
- **Accountability**: Clinician review required; all predictions logged

## Intended Use

- Clinical decision support (alerts for further evaluation)
- Research baseline for sepsis prediction
- Educational tool for ML in healthcare
- **NOT** for standalone diagnosis or real-time continuous monitoring

## Testing

```bash
# Quick test
python test_quick.py

# Full pipeline
python run_full_pipeline.py
```

## License

MIT License

## Citation

If you use this project, please cite:
```
Reyna, M. A., et al. (2019). Early Prediction of Sepsis from Clinical Data. 
Critical Care Medicine.
```

## Disclaimer

This is a research tool. Clinical validation required before hospital deployment. Complements, not replaces, clinical judgment.

---

**Version**: 1.0 | **Last Updated**: February 2026
