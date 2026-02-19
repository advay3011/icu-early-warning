# Model Calibration & Clinical Threshold Optimization Guide

## Overview

This module transforms raw model probabilities into clinically actionable alerts by:
1. Evaluating probability calibration
2. Applying calibration if needed
3. Optimizing decision thresholds for clinical use
4. Recommending evidence-based alert thresholds

## Why Calibration Matters in Medical AI

### Problem: Uncalibrated Probabilities
- Model predicts "70% probability of sepsis"
- But in reality, only 40% of similar cases have sepsis
- Clinical decisions based on false confidence → poor outcomes

### Solution: Probability Calibration
- Ensures predicted probabilities match actual frequencies
- "70% probability" means ~70% of similar cases are positive
- Enables trustworthy clinical decision-making

## Module Components

### 1. Calibration Evaluation

**Brier Score** (primary metric)
- Measures average squared error of probabilities
- Range: 0 (perfect) to 1 (worst)
- Typical medical AI: 0.05-0.20
- Formula: BS = (1/N) × Σ(predicted_prob - actual_label)²

**Calibration Status**
- **Overconfident**: Predicted probabilities too high
  - Example: Model predicts 0.8, but true rate is 0.3
  - Fix: Apply calibration to reduce overconfidence
  
- **Underconfident**: Predicted probabilities too low
  - Example: Model predicts 0.2, but true rate is 0.6
  - Fix: Apply calibration to increase confidence
  
- **Reasonably Calibrated**: Probabilities match reality
  - No calibration needed

### 2. Probability Calibration Methods

#### Isotonic Regression (Recommended)
- More flexible, non-parametric approach
- Better for complex probability distributions
- Requires more data (typically 100+ samples)
- Use when: You have sufficient test data

#### Platt Scaling
- Simpler, parametric approach
- Fits a logistic function to probabilities
- Works with smaller datasets
- Use when: Limited data available

**Implementation**
```python
from sklearn.calibration import CalibratedClassifierCV

calibrator = CalibratedClassifierCV(model, method='isotonic', cv=5)
calibrator.fit(X_train, y_train)
calibrated_probs = calibrator.predict_proba(X_test)[:, 1]
```

### 3. Threshold Optimization

For each probability threshold (0.05 to 0.50):

**Sensitivity (Recall)**
- "Of all sepsis cases, how many do we catch?"
- Formula: TP / (TP + FN)
- Range: 0 to 1 (higher is better for early warning)

**Specificity**
- "Of all non-sepsis cases, how many do we correctly identify?"
- Formula: TN / (TN + FP)
- Range: 0 to 1 (higher is better)

**Precision**
- "Of all alerts, how many are true sepsis cases?"
- Formula: TP / (TP + FP)
- Range: 0 to 1 (higher is better)

**False Positive Rate (FPR)**
- "Of all non-sepsis cases, how many trigger false alarms?"
- Formula: FP / (FP + TN)
- Range: 0 to 1 (lower is better)

**F1 Score**
- Harmonic mean of precision and recall
- Formula: 2 × (precision × recall) / (precision + recall)
- Range: 0 to 1 (higher is better for balanced performance)

### 4. Clinical Threshold Selection

#### High-Sensitivity Threshold
**Purpose**: Catch as many sepsis cases as possible

**Characteristics**
- Lower threshold (e.g., 0.10)
- High sensitivity (e.g., 90%)
- Lower precision (e.g., 20%)
- More false alarms

**Clinical Use Cases**
- Initial screening in ICU
- High-risk patient populations
- When missing sepsis is very costly
- Early warning systems

**Example**
```
Threshold: 0.10
Sensitivity: 90% → Catches 90 of 100 sepsis cases
Precision: 20% → 1 in 5 alerts is true sepsis
FPR: 15% → 15% of non-sepsis patients get false alarms
```

#### Balanced Threshold
**Purpose**: Balance sensitivity and precision

**Characteristics**
- Medium threshold (e.g., 0.25)
- Moderate sensitivity (e.g., 70%)
- Moderate precision (e.g., 40%)
- Reasonable false alarm rate

**Clinical Use Cases**
- Routine ICU monitoring
- Resource-constrained settings
- When both sensitivity and specificity matter
- Practical alert systems

**Example**
```
Threshold: 0.25
Sensitivity: 70% → Catches 70 of 100 sepsis cases
Precision: 40% → 2 in 5 alerts are true sepsis
FPR: 8% → 8% of non-sepsis patients get false alarms
```

#### High-Specificity Threshold
**Purpose**: Minimize false alarms

**Characteristics**
- Higher threshold (e.g., 0.40)
- Lower sensitivity (e.g., 50%)
- Higher precision (e.g., 70%)
- Fewer false alarms

**Clinical Use Cases**
- Diagnostic confirmation (not screening)
- When false alarms are very costly
- Resource-limited settings with strict alert budgets
- Specialist consultation triggers

**Example**
```
Threshold: 0.40
Sensitivity: 50% → Catches 50 of 100 sepsis cases
Precision: 70% → 7 in 10 alerts are true sepsis
FPR: 2% → Only 2% of non-sepsis patients get false alarms
```

## Running the Module

### Quick Test
```bash
icu-early-warning/venv/bin/python -u icu-early-warning/src/calibration_and_thresholds.py
```

### Integration with Training Pipeline
```python
from calibration_and_thresholds import CalibrationAndThresholdOptimizer

# After model training
y_pred_proba = model.predict_proba(X_test)[:, 1]

# Initialize optimizer
optimizer = CalibrationAndThresholdOptimizer(y_test, y_pred_proba, model)

# Run full pipeline
optimizer.evaluate_calibration()
optimizer.apply_calibration(method='isotonic')
optimizer.optimize_thresholds()
clinical_thresholds = optimizer.identify_clinical_thresholds()

# Generate plots
optimizer.plot_calibration_curve('calibration.png')
optimizer.plot_threshold_performance('thresholds.png')
```

## Interpreting Results

### Calibration Curve (Reliability Diagram)
- **X-axis**: Mean predicted probability
- **Y-axis**: Fraction of actual positives
- **Perfect calibration**: Points lie on diagonal line
- **Overconfident**: Points below diagonal (predicts too high)
- **Underconfident**: Points above diagonal (predicts too low)

### Threshold Performance Plots
1. **Sensitivity vs Threshold**: Decreases as threshold increases
2. **Precision vs Threshold**: Increases as threshold increases
3. **F1 Score vs Threshold**: Peaks at optimal balance point
4. **Sensitivity-Specificity Trade-off**: Inverse relationship

## Clinical Decision Framework

### Step 1: Assess Clinical Context
- What is the cost of missing a sepsis case? (High = prioritize sensitivity)
- What is the cost of a false alarm? (High = prioritize specificity)
- What resources are available? (Limited = need balanced threshold)

### Step 2: Choose Threshold Strategy
| Context | Strategy | Threshold | Sensitivity | Precision |
|---------|----------|-----------|-------------|-----------|
| ICU screening | High-sensitivity | 0.10 | 90% | 20% |
| Routine monitoring | Balanced | 0.25 | 70% | 40% |
| Specialist consult | High-specificity | 0.40 | 50% | 70% |

### Step 3: Validate in Clinical Setting
- Pilot test with real clinicians
- Measure alert fatigue (false positive rate)
- Measure missed cases (false negative rate)
- Adjust threshold based on feedback

## Key Takeaways

1. **Calibration is essential**: Uncalibrated probabilities lead to poor clinical decisions
2. **Threshold choice is clinical**: Different settings need different thresholds
3. **Sensitivity matters for early warning**: Catching sepsis is more important than avoiding false alarms
4. **Trade-offs are unavoidable**: You can't maximize both sensitivity and precision
5. **Validation is critical**: Test thresholds with real clinicians before deployment

## References

- Guo, C., & Pleiss, G. (2017). On Calibration of Modern Neural Networks
- Niculescu-Mizil, A., & Caruana, R. (2005). Predicting Good Probabilities with Supervised Learning
- Steyerberg, E. W. (2009). Clinical Prediction Models: A Practical Approach to Development, Validation, and Updating
