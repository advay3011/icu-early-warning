# Evaluation Plan: Research-Grade Protocol

## 1. Data Split Strategy

### Patient-Level Stratified Split
**Rationale**: Prevent data leakage (all hours of a patient go to same split)

**Process**:
1. Identify all unique patients
2. Stratify by sepsis label (sepsis_label = 0 or 1)
3. Randomly split:
   - Train: 80% of patients
   - Validation: 10% of patients
   - Test: 10% of patients

**Example** (1000 patients, 20% sepsis):
- Train: 800 patients (160 sepsis, 640 non-sepsis) → ~100k patient-hours
- Val: 100 patients (20 sepsis, 80 non-sepsis) → ~12.5k patient-hours
- Test: 100 patients (20 sepsis, 80 non-sepsis) → ~12.5k patient-hours

### Class Imbalance Handling
**Training set only**:
- Apply SMOTE (Synthetic Minority Over-sampling Technique)
- Target ratio: 1:1 (equal sepsis and non-sepsis)
- Fit SMOTE on training set, apply to training set only

**Validation/Test sets**:
- Keep original distribution (realistic evaluation)
- Use class weights in loss function if needed

## 2. Evaluation Metrics

### Primary Metrics

#### 2.1 AUROC (Area Under ROC Curve)
- **Definition**: Probability that model ranks random positive higher than random negative
- **Range**: [0, 1] (0.5 = random, 1.0 = perfect)
- **Target**: ≥ 0.80
- **Computation**: sklearn.metrics.roc_auc_score(y_true, y_pred_proba)

#### 2.2 AUPRC (Area Under Precision-Recall Curve)
- **Definition**: Average precision across all recall levels
- **Range**: [0, 1]
- **Target**: ≥ 0.60 (accounting for class imbalance)
- **Computation**: sklearn.metrics.average_precision_score(y_true, y_pred_proba)
- **Why**: More informative than AUROC for imbalanced data

#### 2.3 Sensitivity at Fixed FPR
- **Definition**: True positive rate when false positive rate = 10%
- **Target**: ≥ 0.70
- **Computation**: 
  ```python
  fpr, tpr, _ = roc_curve(y_true, y_pred_proba)
  idx = np.argmin(np.abs(fpr - 0.10))
  sensitivity_at_fpr = tpr[idx]
  ```
- **Clinical relevance**: Acceptable false alarm rate for ICU alerts

### Secondary Metrics

#### 2.4 Median Hours Early (True Positives Only)
- **Definition**: Among patients with sepsis (true positives), median hours before sepsis onset that model crosses alert threshold
- **Target**: ≥ 3 hours
- **Computation**:
  ```python
  for each true positive patient:
      find first hour where risk_score > threshold
      compute hours_before_onset = sepsis_onset_hour - first_alert_hour
  median_hours_early = median(hours_before_onset)
  ```
- **Clinical relevance**: How much lead time does the model provide?

#### 2.5 Calibration Metrics

**Brier Score**:
- **Definition**: Mean squared error between predicted probability and actual outcome
- **Range**: [0, 1] (0 = perfect, 0.25 = random for balanced data)
- **Target**: < 0.15
- **Computation**: sklearn.metrics.brier_score_loss(y_true, y_pred_proba)

**Calibration Curve**:
- **Definition**: Plot of mean predicted probability vs. observed frequency
- **Method**: Divide predictions into bins, compute observed frequency per bin
- **Interpretation**: Diagonal line = perfectly calibrated

#### 2.6 Sensitivity & Specificity
- **Sensitivity**: TP / (TP + FN) — ability to detect sepsis
- **Specificity**: TN / (TN + FP) — ability to avoid false alarms
- **Target**: Sensitivity ≥ 0.70, Specificity ≥ 0.85

## 3. Threshold Selection

### Alert Threshold
- **Default**: 0.50 (standard classification threshold)
- **Optimization**: Can be tuned on validation set to maximize:
  - Sensitivity at fixed FPR, or
  - F1 score, or
  - Clinical utility (cost-benefit analysis)

### Risk Level Classification
```python
if risk_score < 0.33:
    risk_level = "low"
elif risk_score < 0.67:
    risk_level = "medium"
else:
    risk_level = "high"
```

## 4. Baseline Model

### Model Type
**Logistic Regression** (interpretable, fast, good baseline)

**Features**:
- Current vital signs (HR, SBP, DBP, MAP, RR, SpO2, Temp)
- Current labs (WBC, Lactate, Glucose, Creatinine, Platelets, Hemoglobin)
- Rolling statistics (6-hour mean, std, trend for each vital/lab)
- Missingness indicators
- Total missing count

**Total features**: ~60-80 (depending on data availability)

**Hyperparameters**:
- Regularization: L2 (Ridge)
- C (inverse regularization strength): 1.0 (default)
- Class weight: "balanced" (to handle imbalance)

### Baseline Results Expected
- AUROC: 0.75-0.80
- AUPRC: 0.50-0.60
- Sensitivity@FPR=0.10: 0.60-0.70
- Median hours early: 2-3 hours

## 5. Model Upgrade Path

### Phase 2: Hyperparameter Tuning
- Grid search on C parameter
- Evaluate on validation set
- Expected improvement: +0.02-0.05 AUROC

### Phase 3: Gradient Boosting
- XGBoost or LightGBM
- Captures non-linear relationships
- Expected improvement: +0.05-0.10 AUROC

### Phase 4: Feature Selection
- Recursive feature elimination (RFE)
- SHAP-based feature importance
- Remove low-importance features
- Expected improvement: +0.02-0.05 AUROC, better interpretability

## 6. Validation Strategy

### Cross-Validation
- **Type**: 5-fold stratified cross-validation on training set
- **Purpose**: Estimate generalization error, detect overfitting
- **Reporting**: Mean ± std of each metric across folds

### Validation Set Evaluation
- **Purpose**: Hyperparameter tuning, threshold selection
- **Reporting**: Single metric values (not averaged)

### Test Set Evaluation
- **Purpose**: Final model assessment (report only once)
- **Reporting**: Single metric values with 95% confidence intervals

## 7. Reporting Format

### Summary Table
```
Metric                          | Train  | Val    | Test   | Target
AUROC                           | 0.82   | 0.80   | 0.79   | ≥0.80
AUPRC                           | 0.68   | 0.62   | 0.61   | ≥0.60
Sensitivity @ FPR=0.10          | 0.75   | 0.72   | 0.71   | ≥0.70
Median Hours Early (TP only)    | 3.2h   | 3.0h   | 2.9h   | ≥3.0h
Brier Score                     | 0.12   | 0.13   | 0.14   | <0.15
Sensitivity (at threshold=0.5)  | 0.73   | 0.70   | 0.69   | ≥0.70
Specificity (at threshold=0.5)  | 0.87   | 0.85   | 0.84   | ≥0.85
```

### Detailed Metrics
- ROC curve (plot)
- Precision-Recall curve (plot)
- Calibration curve (plot)
- Confusion matrix (test set)
- Feature importance (top 20 features)

## 8. Clinical Interpretation

### Per-Patient Timeline
For each test patient, generate:
- Hour-by-hour risk score
- Risk level (low/medium/high)
- Alert events (when risk crosses threshold)
- Hours before sepsis onset (if applicable)
- Top contributing features at each alert

### Example Output
```
Patient p000042 (Sepsis onset: Hour 24)
Hour | Risk Score | Risk Level | Alert | Top Features
...
20   | 0.35       | Low        | No    | HR_mean_6h, Temp
21   | 0.42       | Medium     | No    | HR_mean_6h, Lactate, WBC
22   | 0.58       | High       | YES   | Lactate, HR_trend_6h, WBC
23   | 0.72       | High       | YES   | Lactate, HR_trend_6h, Temp_trend_6h
24   | 0.81       | High       | YES   | Lactate, HR_trend_6h, WBC (SEPSIS ONSET)
```

## 9. Success Criteria

**Model is considered successful if**:
- ✓ AUROC ≥ 0.80 on test set
- ✓ AUPRC ≥ 0.60 on test set
- ✓ Sensitivity ≥ 0.70 at FPR ≤ 0.10
- ✓ Median hours early ≥ 3 hours
- ✓ Brier score < 0.15
- ✓ Top 5 features are clinically interpretable
- ✓ No evidence of overfitting (train/val/test metrics similar)
