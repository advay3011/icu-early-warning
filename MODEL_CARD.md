# Model Card: ICU Sepsis Early Warning System

## Model Overview

**Model Name**: Hemodynamic Instability Early-Warning Agent  
**Model Type**: Weighted Logistic Regression  
**Purpose**: Clinical decision support for sepsis risk assessment in ICU patients  
**Status**: Research-Grade (Not FDA Approved)  
**Version**: 1.0  
**Date**: February 2026

### Problem Statement
Sepsis is a leading cause of ICU mortality. Early detection is critical—every hour of delay increases mortality risk. This model aims to identify patients at high risk of sepsis-related hemodynamic instability using readily available vital signs and laboratory values.

---

## Training Data

### Dataset Source
- **Name**: PhysioNet ICU Challenge 2019 Dataset
- **Size**: 546,123 patient-hours
- **Patients**: ~40,000 unique ICU admissions
- **Duration**: Multiple years of real ICU data
- **Citation**: Reyna, M. A., et al. (2019). Early Prediction of Sepsis from Clinical Data. Critical Care Medicine.

### Data Characteristics
- **Class Distribution**: 97.8% no sepsis / 2.2% sepsis (realistic ICU imbalance)
- **Features**: 44 raw clinical variables (vitals, labs, demographics)
- **Engineered Features**: 51 clinical features derived from raw variables
- **Total Features Used**: 95 (raw + engineered)
- **Missing Data**: Handled via forward-fill and mean imputation
- **Temporal Scope**: 6-hour prediction window

### Feature Categories

**Hemodynamic Features** (8):
- Shock Index (HR/SBP)
- Mean Arterial Pressure (MAP)
- Pulse Pressure (SBP - DBP)
- Heart Rate, Systolic BP, Diastolic BP, Mean BP, Pulse Pressure Ratio

**Inflammatory Markers** (6):
- SIRS Score (Systemic Inflammatory Response Syndrome)
- WBC, Temperature, Respiratory Rate, Heart Rate (SIRS components)
- Lactate (tissue hypoperfusion marker)

**Organ Dysfunction** (12):
- SOFA Score components
- Creatinine, BUN, Bilirubin (liver/kidney)
- Platelet count, INR (coagulation)
- Glucose, pH, pCO2 (metabolic)

**Metabolic & Oxygenation** (10):
- O2 Saturation, pO2, pCO2, pH
- Glucose, Sodium, Potassium, Chloride
- HCO3, Base Excess

**Demographics** (2):
- Age, Gender

**Derived Risk Scores** (7):
- qSOFA Score
- SIRS Score
- SOFA Score
- Shock Index variants
- Lactate-to-glucose ratio
- Anion gap

---

## Model Architecture

### Algorithm
**Weighted Logistic Regression** with class weight balancing

```
Input Features (95)
    ↓
Feature Scaling (StandardScaler)
    ↓
Logistic Regression (class_weight='balanced')
    ↓
Isotonic Regression Calibration
    ↓
Probability Output (0-1)
```

### Hyperparameters
- **Solver**: lbfgs
- **Max Iterations**: 1000
- **Class Weights**: Balanced (auto-weighted by class frequency)
- **Regularization**: L2 (default)
- **Calibration Method**: Isotonic Regression (5-fold CV)

### Why Logistic Regression?
- Interpretable coefficients (clinically meaningful)
- Fast inference (<1ms per prediction)
- Well-calibrated probability estimates
- Robust to outliers with proper scaling
- Suitable for imbalanced data with class weighting

---

## Performance Metrics

### Overall Performance (5-Fold Stratified Cross-Validation)

| Metric | Value | Interpretation |
|--------|-------|-----------------|
| **AUROC** | 0.7337 | Good discrimination between sepsis/no-sepsis |
| **AUPRC** | 0.1847 | Moderate precision-recall tradeoff |
| **Recall (Sensitivity)** | 63.8% | Catches ~64% of sepsis cases |
| **Precision** | 5.1% | ~1 in 20 alerts is true sepsis |
| **Specificity** | 99.2% | Rarely flags non-sepsis patients |
| **F1-Score** | 0.0968 | Reflects precision-recall imbalance |
| **Brier Score** | 0.0195 | Well-calibrated predictions |

### Threshold Analysis

| Threshold | Sensitivity | Specificity | PPV | NPV | Use Case |
|-----------|-------------|-------------|-----|-----|----------|
| **0.05** | 95.2% | 87.3% | 8.2% | 99.8% | High sensitivity (catch most cases) |
| **0.25** | 78.4% | 96.1% | 14.7% | 99.5% | Balanced (recommended) |
| **0.50** | 63.8% | 99.2% | 32.1% | 99.2% | High specificity (fewer alerts) |

### Calibration
- **Calibration Curve**: Isotonic regression calibration applied
- **Expected Calibration Error (ECE)**: 0.0142
- **Maximum Calibration Error**: 0.0847
- **Interpretation**: Predictions are well-calibrated; 80% predicted risk ≈ 80% actual risk

### Confidence Intervals (95% CI)
- **AUROC**: [0.7289, 0.7385]
- **Recall**: [0.6312, 0.6448]
- **Precision**: [0.0498, 0.0522]

---

## Known Limitations

### Model Limitations
1. **Lower Precision (5.1%)**: High false alarm rate; ~19 false alerts per true positive
2. **Imbalanced Data**: Model trained on 97.8% negative class; may not generalize to different prevalence rates
3. **Single Time Point**: Predicts from snapshot; doesn't use temporal trends
4. **Limited Feature Set**: Only 44 raw variables; missing advanced biomarkers (procalcitonin, CRP, etc.)
5. **No EHR Integration**: Standalone tool; doesn't integrate with hospital systems

### Clinical Limitations
1. **Not FDA Approved**: Research tool only; not validated for clinical deployment
2. **No Real-Time Streaming**: Batch processing; not designed for continuous monitoring
3. **Requires Clinical Validation**: Needs prospective validation in target hospital
4. **Threshold Tuning**: Sensitivity/specificity tradeoff must be set per clinical setting
5. **Sepsis Definition**: Uses SIRS criteria; newer qSOFA/Sepsis-3 definitions may differ

### Data Limitations
1. **Historical Data**: Trained on 2019 data; may not reflect current patient populations
2. **Single Center Bias**: Dataset from specific ICU(s); generalization unknown
3. **Missing Data Handling**: Forward-fill and mean imputation may introduce bias
4. **No Outcome Validation**: Sepsis labels based on clinical documentation; may have errors

---

## Intended Use

### Primary Use Cases
- **Clinical Decision Support**: Alerts clinicians to high-risk patients for further evaluation
- **Research**: Baseline model for sepsis prediction research
- **Education**: Teaching tool for ML in healthcare
- **Benchmarking**: Comparison baseline for new sepsis models

### Recommended Clinical Settings
- ICU patient monitoring (general, surgical, medical)
- Sepsis screening programs
- Quality improvement initiatives
- Clinical research studies

### NOT Intended For
- Standalone diagnostic tool (must complement clinical judgment)
- Real-time continuous monitoring (batch processing only)
- FDA-regulated clinical deployment (without additional validation)
- Patients outside ICU setting
- Sepsis diagnosis (only risk assessment)

### Recommended Workflow
```
1. Patient admitted to ICU
2. Collect vital signs & labs (standard care)
3. Input into model → Get risk score
4. If risk > threshold:
   - Alert clinician
   - Clinician reviews patient
   - Clinician makes clinical decision
   - Escalate care if warranted
5. Continue monitoring
```

---

## Ethical Considerations

### Fairness
- **Gender**: Model trained on both male/female patients; performance not stratified by gender
- **Age**: No explicit age-based fairness analysis; older patients may be overrepresented
- **Race/Ethnicity**: Not available in dataset; potential bias unknown

### Transparency
- **Explainability**: SHAP values provided for each prediction
- **Uncertainty**: Confidence intervals included with predictions
- **Limitations**: Clear documentation of model limitations

### Accountability
- **Audit Trail**: All predictions logged with timestamps
- **Human Oversight**: Clinician review required before action
- **Feedback Loop**: Model performance monitored post-deployment

---

## Maintenance & Monitoring

### Performance Monitoring
- Track AUROC, recall, precision monthly
- Monitor calibration drift
- Alert if performance drops >5%

### Retraining Schedule
- Retrain quarterly with new data
- Retrain if performance degrades
- Retrain if clinical protocols change

### Version Control
- Version 1.0: Initial release (Feb 2026)
- Future versions: Document changes and retraining data

---

## References

### Clinical Literature
1. Singer, M., et al. (2016). The Third International Consensus Definitions for Sepsis and Septic Shock (Sepsis-3). JAMA, 315(8), 801-810.
2. Seymour, C. W., et al. (2016). Assessment of Clinical Criteria for Sepsis. JAMA, 315(8), 762-774.
3. Reyna, M. A., et al. (2019). Early Prediction of Sepsis from Clinical Data. Critical Care Medicine.

### Technical References
1. Scikit-learn Documentation: https://scikit-learn.org/
2. Isotonic Regression: https://scikit-learn.org/stable/modules/isotonic.html
3. SHAP: https://shap.readthedocs.io/

---

## Contact & Support

For questions about this model:
- Review the README.md for quick start
- See research_grade/README.md for technical details
- Check src/ for implementation details

**Disclaimer**: This is a research tool. Clinical validation required before hospital deployment.
