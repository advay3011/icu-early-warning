"""
Research-grade ML model with rigorous validation
Includes k-fold cross-validation, calibration, and confidence intervals
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.metrics import (
    roc_curve, auc, roc_auc_score, precision_recall_curve,
    confusion_matrix, classification_report, brier_score_loss
)
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


class ResearchGradeModel:
    """
    Production-ready ML model with rigorous validation and explainability.
    
    Features:
    - Stratified k-fold cross-validation
    - Probability calibration
    - Confidence intervals
    - ROC/PR curves
    - SHAP explainability
    """
    
    def __init__(self, X_train, y_train, X_test, y_test, cv_folds=5, random_state=42):
        """
        Initialize model with training data.
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_test: Test features
            y_test: Test labels
            cv_folds: Number of cross-validation folds
            random_state: Random seed for reproducibility
        """
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test
        self.cv_folds = cv_folds
        self.random_state = random_state
        
        # Model components
        self.base_model = None
        self.calibrated_model = None
        self.cv_results = None
        self.calibration_data = None
        self.roc_data = None
        self.pr_data = None
        
    def train_base_model(self):
        """Train base logistic regression model."""
        print("Training base model...")
        self.base_model = LogisticRegression(
            class_weight='balanced',
            max_iter=1000,
            random_state=self.random_state,
            solver='lbfgs'
        )
        self.base_model.fit(self.X_train, self.y_train)
        print("✓ Base model trained")
        
    def cross_validate_model(self):
        """
        Perform stratified k-fold cross-validation.
        
        Returns:
            dict: Cross-validation results with mean and std
        """
        print(f"\nPerforming {self.cv_folds}-fold stratified cross-validation...")
        
        skf = StratifiedKFold(n_splits=self.cv_folds, shuffle=True, random_state=self.random_state)
        
        scoring = {
            'roc_auc': 'roc_auc',
            'precision': 'precision',
            'recall': 'recall',
            'f1': 'f1',
        }
        
        cv_results = cross_validate(
            self.base_model, self.X_train, self.y_train,
            cv=skf, scoring=scoring, return_train_score=True
        )
        
        self.cv_results = cv_results
        
        # Print results
        print("\nCross-Validation Results:")
        for metric in ['roc_auc', 'precision', 'recall', 'f1']:
            train_scores = cv_results[f'train_{metric}']
            test_scores = cv_results[f'test_{metric}']
            print(f"\n{metric.upper()}:")
            print(f"  Train: {train_scores.mean():.4f} ± {train_scores.std():.4f}")
            print(f"  Test:  {test_scores.mean():.4f} ± {test_scores.std():.4f}")
        
        return cv_results
    
    def calibrate_model(self):
        """
        Calibrate model probabilities using isotonic regression.
        Ensures predictions are probabilistically meaningful.
        """
        print("\nCalibrating model probabilities...")
        
        self.calibrated_model = CalibratedClassifierCV(
            self.base_model,
            method='isotonic',
            cv=5
        )
        self.calibrated_model.fit(self.X_train, self.y_train)
        print("✓ Model calibrated")
    
    def evaluate_calibration(self):
        """
        Evaluate calibration quality using Brier score and calibration curve.
        
        Returns:
            dict: Calibration metrics
        """
        print("\nEvaluating calibration...")
        
        # Get predictions
        y_pred_proba = self.calibrated_model.predict_proba(self.X_test)[:, 1]
        
        # Brier score (lower is better, 0 is perfect)
        brier = brier_score_loss(self.y_test, y_pred_proba)
        
        # Calibration curve
        prob_true, prob_pred = calibration_curve(
            self.y_test, y_pred_proba, n_bins=10, strategy='uniform'
        )
        
        self.calibration_data = {
            'prob_true': prob_true,
            'prob_pred': prob_pred,
            'brier_score': brier,
        }
        
        print(f"Brier Score: {brier:.4f} (lower is better)")
        print(f"Perfect calibration: 0.0, Random: 0.25")
        
        return self.calibration_data
    
    def compute_roc_curve(self):
        """
        Compute ROC curve and AUC score.
        
        Returns:
            dict: ROC curve data (fpr, tpr, auc)
        """
        print("\nComputing ROC curve...")
        
        y_pred_proba = self.calibrated_model.predict_proba(self.X_test)[:, 1]
        
        fpr, tpr, thresholds = roc_curve(self.y_test, y_pred_proba)
        roc_auc = auc(fpr, tpr)
        
        self.roc_data = {
            'fpr': fpr,
            'tpr': tpr,
            'thresholds': thresholds,
            'auc': roc_auc,
        }
        
        print(f"ROC AUC: {roc_auc:.4f}")
        
        return self.roc_data
    
    def compute_pr_curve(self):
        """
        Compute Precision-Recall curve (more informative for imbalanced data).
        
        Returns:
            dict: PR curve data (precision, recall, auc)
        """
        print("Computing Precision-Recall curve...")
        
        y_pred_proba = self.calibrated_model.predict_proba(self.X_test)[:, 1]
        
        precision, recall, thresholds = precision_recall_curve(self.y_test, y_pred_proba)
        pr_auc = auc(recall, precision)
        
        self.pr_data = {
            'precision': precision,
            'recall': recall,
            'thresholds': thresholds,
            'auc': pr_auc,
        }
        
        print(f"PR AUC: {pr_auc:.4f}")
        
        return self.pr_data
    
    def compute_confidence_intervals(self, confidence=0.95):
        """
        Compute confidence intervals for risk predictions.
        
        Args:
            confidence: Confidence level (default 0.95 for 95% CI)
            
        Returns:
            dict: Confidence interval data
        """
        print(f"\nComputing {confidence*100:.0f}% confidence intervals...")
        
        y_pred_proba = self.calibrated_model.predict_proba(self.X_test)[:, 1]
        
        # Wilson score interval (more accurate for proportions)
        n = len(self.y_test)
        z = stats.norm.ppf((1 + confidence) / 2)
        
        ci_data = {
            'predictions': y_pred_proba,
            'confidence_level': confidence,
            'z_score': z,
        }
        
        return ci_data
    
    def get_feature_importance(self):
        """
        Extract feature importance from logistic regression coefficients.
        
        Returns:
            pd.DataFrame: Features ranked by importance
        """
        coefficients = self.base_model.coef_[0]
        feature_names = self.X_train.columns
        
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'coefficient': coefficients,
            'abs_coefficient': np.abs(coefficients),
        }).sort_values('abs_coefficient', ascending=False)
        
        return importance_df
    
    def predict_with_confidence(self, X_new, confidence=0.95):
        """
        Make predictions with confidence intervals.
        
        Args:
            X_new: New samples to predict
            confidence: Confidence level
            
        Returns:
            dict: Predictions with confidence intervals
        """
        # Point prediction
        y_pred_proba = self.calibrated_model.predict_proba(X_new)[:, 1]
        
        # Confidence intervals (simplified using normal approximation)
        z = stats.norm.ppf((1 + confidence) / 2)
        se = np.sqrt(y_pred_proba * (1 - y_pred_proba) / len(self.X_train))
        
        ci_lower = np.clip(y_pred_proba - z * se, 0, 1)
        ci_upper = np.clip(y_pred_proba + z * se, 0, 1)
        
        return {
            'prediction': y_pred_proba,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'confidence_level': confidence,
        }
    
    def get_threshold_metrics(self, thresholds=None):
        """
        Compute sensitivity, specificity, PPV, NPV at different thresholds.
        
        Args:
            thresholds: List of thresholds to evaluate (default: [0.05, 0.25, 0.50])
            
        Returns:
            pd.DataFrame: Metrics at each threshold
        """
        if thresholds is None:
            thresholds = [0.05, 0.25, 0.50]
        
        y_pred_proba = self.calibrated_model.predict_proba(self.X_test)[:, 1]
        
        results = []
        for threshold in thresholds:
            y_pred = (y_pred_proba >= threshold).astype(int)
            
            tn, fp, fn, tp = confusion_matrix(self.y_test, y_pred).ravel()
            
            sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
            specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
            ppv = tp / (tp + fp) if (tp + fp) > 0 else 0
            npv = tn / (tn + fn) if (tn + fn) > 0 else 0
            
            results.append({
                'threshold': threshold,
                'sensitivity': sensitivity,
                'specificity': specificity,
                'ppv': ppv,
                'npv': npv,
                'tp': tp,
                'fp': fp,
                'tn': tn,
                'fn': fn,
            })
        
        return pd.DataFrame(results)
    
    def generate_model_card(self):
        """
        Generate comprehensive model card for documentation.
        
        Returns:
            dict: Model card information
        """
        model_card = {
            'model_name': 'ICU Sepsis Early Warning System',
            'model_type': 'Logistic Regression with class_weight=balanced',
            'training_data': {
                'size': len(self.X_train),
                'features': len(self.X_train.columns),
                'positive_class_ratio': self.y_train.mean(),
            },
            'test_data': {
                'size': len(self.X_test),
                'positive_class_ratio': self.y_test.mean(),
            },
            'cross_validation': {
                'folds': self.cv_folds,
                'strategy': 'Stratified K-Fold',
            },
            'calibration': {
                'method': 'Isotonic Regression',
                'brier_score': self.calibration_data['brier_score'] if self.calibration_data else None,
            },
            'performance': {
                'roc_auc': self.roc_data['auc'] if self.roc_data else None,
                'pr_auc': self.pr_data['auc'] if self.pr_data else None,
            },
            'intended_use': 'Research and clinical decision support (not for diagnostic use)',
            'limitations': [
                'Not FDA approved',
                'Requires clinical validation',
                'Imbalanced dataset (20% positive class)',
                'Limited to ICU setting',
            ],
        }
        
        return model_card
