"""
Model Calibration & Clinical Threshold Optimization
Transforms model probabilities into clinically actionable alerts
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.calibration import calibration_curve, CalibratedClassifierCV
from sklearn.metrics import (
    brier_score_loss, roc_curve, precision_recall_curve,
    precision_score, recall_score, f1_score, confusion_matrix
)
from typing import Dict, Tuple, List


class CalibrationAndThresholdOptimizer:
    """Calibrate model probabilities and optimize clinical thresholds."""
    
    def __init__(self, y_true: np.ndarray, y_pred_proba: np.ndarray, model=None):
        """
        Initialize optimizer.
        
        Args:
            y_true: True labels
            y_pred_proba: Predicted probabilities (positive class)
            model: Fitted model for calibration (optional)
        """
        self.y_true = y_true
        self.y_pred_proba = y_pred_proba
        self.model = model
        
        self.y_pred_proba_calibrated = None
        self.calibrator = None
        self.calibration_results = {}
        self.threshold_results = {}
    
    def evaluate_calibration(self) -> Dict:
        """
        Evaluate model calibration using reliability diagram and Brier score.
        
        Returns:
            Dictionary with calibration metrics
        """
        print("\n" + "=" * 80)
        print("STEP 1: CALIBRATION EVALUATION")
        print("=" * 80)
        
        # Compute Brier score (lower is better, 0 = perfect)
        brier_uncalibrated = brier_score_loss(self.y_true, self.y_pred_proba)
        
        print(f"\nUncalibrated Model:")
        print(f"  Brier Score: {brier_uncalibrated:.4f}")
        print(f"  (Range: 0 = perfect, 1 = worst)")
        
        # Compute calibration curve
        prob_true, prob_pred = calibration_curve(
            self.y_true, self.y_pred_proba, n_bins=10, strategy='uniform'
        )
        
        # Analyze calibration
        mean_predicted_prob = self.y_pred_proba.mean()
        mean_true_prob = self.y_true.mean()
        
        print(f"\nCalibration Analysis:")
        print(f"  Mean predicted probability: {mean_predicted_prob:.4f}")
        print(f"  Mean true probability (prevalence): {mean_true_prob:.4f}")
        
        if mean_predicted_prob > mean_true_prob * 1.5:
            calibration_status = "OVERCONFIDENT"
            print(f"  Status: {calibration_status} (predicts too high probabilities)")
        elif mean_predicted_prob < mean_true_prob * 0.5:
            calibration_status = "UNDERCONFIDENT"
            print(f"  Status: {calibration_status} (predicts too low probabilities)")
        else:
            calibration_status = "REASONABLY CALIBRATED"
            print(f"  Status: {calibration_status}")
        
        self.calibration_results = {
            'brier_uncalibrated': brier_uncalibrated,
            'prob_true': prob_true,
            'prob_pred': prob_pred,
            'mean_predicted': mean_predicted_prob,
            'mean_true': mean_true_prob,
            'status': calibration_status
        }
        
        return self.calibration_results
    
    def apply_calibration(self, method: str = 'isotonic') -> Dict:
        """
        Apply probability calibration if needed.
        
        Args:
            method: 'platt' (Platt scaling) or 'isotonic' (isotonic regression)
        
        Returns:
            Dictionary with calibration results
        """
        print("\n" + "=" * 80)
        print("STEP 2: PROBABILITY CALIBRATION")
        print("=" * 80)
        
        if self.model is None:
            print("\n⚠ Warning: Model not provided, skipping calibration")
            print("  (Calibration requires fitted model for proper cross-validation)")
            self.y_pred_proba_calibrated = self.y_pred_proba
            return self.calibration_results
        
        print(f"\nApplying {method} calibration...")
        
        # Apply calibration
        self.calibrator = CalibratedClassifierCV(
            self.model, method=method, cv=5
        )
        self.calibrator.fit(self.y_true.reshape(-1, 1), self.y_true)
        self.y_pred_proba_calibrated = self.calibrator.predict_proba(
            self.y_true.reshape(-1, 1)
        )[:, 1]
        
        # Compute calibrated Brier score
        brier_calibrated = brier_score_loss(self.y_true, self.y_pred_proba_calibrated)
        
        print(f"\nCalibration Results:")
        print(f"  Brier Score (before): {self.calibration_results['brier_uncalibrated']:.4f}")
        print(f"  Brier Score (after):  {brier_calibrated:.4f}")
        print(f"  Improvement: {self.calibration_results['brier_uncalibrated'] - brier_calibrated:.4f}")
        
        self.calibration_results['brier_calibrated'] = brier_calibrated
        self.calibration_results['method'] = method
        
        return self.calibration_results
    
    def optimize_thresholds(self, thresholds: List[float] = None) -> pd.DataFrame:
        """
        Evaluate performance at multiple probability thresholds.
        
        Args:
            thresholds: List of thresholds to evaluate (default: 0.05 to 0.50)
        
        Returns:
            DataFrame with threshold performance metrics
        """
        print("\n" + "=" * 80)
        print("STEP 3: THRESHOLD OPTIMIZATION")
        print("=" * 80)
        
        if thresholds is None:
            thresholds = np.arange(0.05, 0.51, 0.05)
        
        # Use calibrated probabilities if available
        proba = self.y_pred_proba_calibrated if self.y_pred_proba_calibrated is not None else self.y_pred_proba
        
        results = []
        
        print(f"\nEvaluating {len(thresholds)} thresholds...")
        
        for threshold in thresholds:
            y_pred = (proba >= threshold).astype(int)
            
            # Compute metrics
            tn, fp, fn, tp = confusion_matrix(self.y_true, y_pred).ravel()
            
            sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0  # Recall
            specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
            f1 = 2 * (precision * sensitivity) / (precision + sensitivity) if (precision + sensitivity) > 0 else 0
            
            results.append({
                'Threshold': threshold,
                'Sensitivity (Recall)': sensitivity,
                'Specificity': specificity,
                'Precision': precision,
                'False Positive Rate': fpr,
                'F1 Score': f1,
                'TP': tp,
                'FP': fp,
                'TN': tn,
                'FN': fn
            })
        
        self.threshold_results = pd.DataFrame(results)
        
        print("\nThreshold Performance Table:")
        print(self.threshold_results[['Threshold', 'Sensitivity (Recall)', 'Precision', 'F1 Score', 'False Positive Rate']].to_string(index=False))
        
        return self.threshold_results
    
    def identify_clinical_thresholds(self) -> Dict:
        """
        Identify two clinically meaningful thresholds.
        
        Returns:
            Dictionary with recommended thresholds and rationale
        """
        print("\n" + "=" * 80)
        print("STEP 4: CLINICAL THRESHOLD SELECTION")
        print("=" * 80)
        
        if self.threshold_results.empty:
            print("⚠ Run optimize_thresholds() first")
            return {}
        
        # High-sensitivity threshold (maximize recall, minimize missed cases)
        high_sensitivity_idx = self.threshold_results['Sensitivity (Recall)'].idxmax()
        high_sensitivity_threshold = self.threshold_results.loc[high_sensitivity_idx]
        
        # Balanced threshold (maximize F1 score)
        balanced_idx = self.threshold_results['F1 Score'].idxmax()
        balanced_threshold = self.threshold_results.loc[balanced_idx]
        
        print("\n1️⃣  HIGH-SENSITIVITY THRESHOLD (Maximize Recall)")
        print("   Purpose: Catch as many sepsis cases as possible")
        print("   Clinical Use: Initial screening, high-risk patients")
        print(f"\n   Threshold: {high_sensitivity_threshold['Threshold']:.2f}")
        print(f"   Sensitivity: {high_sensitivity_threshold['Sensitivity (Recall)']:.1%}")
        print(f"   Specificity: {high_sensitivity_threshold['Specificity']:.1%}")
        print(f"   Precision: {high_sensitivity_threshold['Precision']:.1%}")
        print(f"   False Positive Rate: {high_sensitivity_threshold['False Positive Rate']:.1%}")
        print(f"\n   Interpretation:")
        print(f"   • Catches {high_sensitivity_threshold['Sensitivity (Recall)']:.1%} of sepsis cases")
        print(f"   • {high_sensitivity_threshold['False Positive Rate']:.1%} false alarm rate")
        print(f"   • Better to over-alert than miss sepsis")
        
        print("\n" + "-" * 80)
        
        print("\n2️⃣  BALANCED THRESHOLD (Maximize F1 Score)")
        print("   Purpose: Balance sensitivity and precision")
        print("   Clinical Use: Routine monitoring, resource-constrained settings")
        print(f"\n   Threshold: {balanced_threshold['Threshold']:.2f}")
        print(f"   Sensitivity: {balanced_threshold['Sensitivity (Recall)']:.1%}")
        print(f"   Specificity: {balanced_threshold['Specificity']:.1%}")
        print(f"   Precision: {balanced_threshold['Precision']:.1%}")
        print(f"   False Positive Rate: {balanced_threshold['False Positive Rate']:.1%}")
        print(f"   F1 Score: {balanced_threshold['F1 Score']:.4f}")
        print(f"\n   Interpretation:")
        print(f"   • Balanced trade-off between catching cases and false alarms")
        print(f"   • {balanced_threshold['Sensitivity (Recall)']:.1%} sensitivity, {balanced_threshold['Precision']:.1%} precision")
        print(f"   • Suitable for resource-limited settings")
        
        clinical_thresholds = {
            'high_sensitivity': {
                'threshold': high_sensitivity_threshold['Threshold'],
                'sensitivity': high_sensitivity_threshold['Sensitivity (Recall)'],
                'specificity': high_sensitivity_threshold['Specificity'],
                'precision': high_sensitivity_threshold['Precision'],
                'fpr': high_sensitivity_threshold['False Positive Rate'],
                'use_case': 'Initial screening, high-risk patients'
            },
            'balanced': {
                'threshold': balanced_threshold['Threshold'],
                'sensitivity': balanced_threshold['Sensitivity (Recall)'],
                'specificity': balanced_threshold['Specificity'],
                'precision': balanced_threshold['Precision'],
                'fpr': balanced_threshold['False Positive Rate'],
                'f1': balanced_threshold['F1 Score'],
                'use_case': 'Routine monitoring, resource-constrained'
            }
        }
        
        return clinical_thresholds
    
    def plot_calibration_curve(self, save_path: str = None):
        """Plot calibration curve (reliability diagram)."""
        if not self.calibration_results:
            print("⚠ Run evaluate_calibration() first")
            return
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Plot calibration curve
        prob_true = self.calibration_results['prob_true']
        prob_pred = self.calibration_results['prob_pred']
        
        ax.plot(prob_pred, prob_true, marker='o', linewidth=2, label='Model', markersize=8)
        ax.plot([0, 1], [0, 1], 'k--', linewidth=2, label='Perfect Calibration')
        
        ax.set_xlabel('Mean Predicted Probability', fontsize=12, fontweight='bold')
        ax.set_ylabel('Fraction of Positives', fontsize=12, fontweight='bold')
        ax.set_title('Calibration Curve (Reliability Diagram)', fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0, 1])
        ax.set_ylim([0, 1])
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Calibration curve saved to {save_path}")
        
        return fig
    
    def plot_threshold_performance(self, save_path: str = None):
        """Plot threshold vs performance metrics."""
        if self.threshold_results.empty:
            print("⚠ Run optimize_thresholds() first")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        thresholds = self.threshold_results['Threshold']
        
        # Plot 1: Sensitivity vs Threshold
        axes[0, 0].plot(thresholds, self.threshold_results['Sensitivity (Recall)'], 'o-', linewidth=2, markersize=6, color='#27ae60')
        axes[0, 0].set_xlabel('Threshold', fontweight='bold')
        axes[0, 0].set_ylabel('Sensitivity (Recall)', fontweight='bold')
        axes[0, 0].set_title('Sensitivity vs Threshold', fontweight='bold')
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].set_ylim([0, 1])
        
        # Plot 2: Precision vs Threshold
        axes[0, 1].plot(thresholds, self.threshold_results['Precision'], 'o-', linewidth=2, markersize=6, color='#e74c3c')
        axes[0, 1].set_xlabel('Threshold', fontweight='bold')
        axes[0, 1].set_ylabel('Precision', fontweight='bold')
        axes[0, 1].set_title('Precision vs Threshold', fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].set_ylim([0, 1])
        
        # Plot 3: F1 Score vs Threshold
        axes[1, 0].plot(thresholds, self.threshold_results['F1 Score'], 'o-', linewidth=2, markersize=6, color='#3498db')
        axes[1, 0].set_xlabel('Threshold', fontweight='bold')
        axes[1, 0].set_ylabel('F1 Score', fontweight='bold')
        axes[1, 0].set_title('F1 Score vs Threshold', fontweight='bold')
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].set_ylim([0, 1])
        
        # Plot 4: Sensitivity-Specificity Trade-off
        axes[1, 1].plot(thresholds, self.threshold_results['Sensitivity (Recall)'], 'o-', linewidth=2, markersize=6, label='Sensitivity', color='#27ae60')
        axes[1, 1].plot(thresholds, self.threshold_results['Specificity'], 's-', linewidth=2, markersize=6, label='Specificity', color='#9b59b6')
        axes[1, 1].set_xlabel('Threshold', fontweight='bold')
        axes[1, 1].set_ylabel('Rate', fontweight='bold')
        axes[1, 1].set_title('Sensitivity-Specificity Trade-off', fontweight='bold')
        axes[1, 1].legend(fontsize=10)
        axes[1, 1].grid(True, alpha=0.3)
        axes[1, 1].set_ylim([0, 1])
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Threshold performance plot saved to {save_path}")
        
        return fig
    
    def print_calibration_explanation(self):
        """Print explanation of calibration importance."""
        print("\n" + "=" * 80)
        print("WHY CALIBRATION MATTERS IN MEDICAL AI")
        print("=" * 80)
        
        print("""
1. PROBABILITY INTERPRETATION
   ──────────────────────────
   • Uncalibrated model: "70% probability" might actually mean 50% or 90%
   • Calibrated model: "70% probability" means ~70% of similar cases are positive
   • Clinical decision-making requires trustworthy probabilities
   
2. THRESHOLD SELECTION DEPENDS ON CALIBRATION
   ──────────────────────────────────────────
   • If model is overconfident: threshold of 0.5 might catch too few cases
   • If model is underconfident: threshold of 0.5 might trigger too many alerts
   • Calibration ensures thresholds have consistent meaning
   
3. BRIER SCORE MEASURES CALIBRATION QUALITY
   ────────────────────────────────────────
   • Brier Score = mean squared error of probabilities
   • Range: 0 (perfect) to 1 (worst)
   • Typical medical AI: 0.05-0.20
   • Improvement after calibration indicates poor initial calibration
   
4. CLINICAL RISK TOLERANCE DRIVES THRESHOLD CHOICE
   ───────────────────────────────────────────────
   
   HIGH-SENSITIVITY THRESHOLD (Low threshold, e.g., 0.10):
   ✓ Catches more sepsis cases (high recall)
   ✗ More false alarms (low precision)
   → Use when: Missing sepsis is very costly (ICU setting)
   
   BALANCED THRESHOLD (Medium threshold, e.g., 0.25):
   ✓ Reasonable balance of sensitivity and precision
   ✓ Fewer false alarms than high-sensitivity
   → Use when: Resources are limited, need practical alerts
   
   HIGH-SPECIFICITY THRESHOLD (High threshold, e.g., 0.40):
   ✓ Fewer false alarms (high precision)
   ✗ Misses more sepsis cases (low recall)
   → Use when: False alarms are very costly (e.g., unnecessary interventions)
   
5. MEDICAL AI REQUIRES DIFFERENT THRESHOLDS THAN GENERAL ML
   ─────────────────────────────────────────────────────────
   • General ML: Optimize for accuracy (balanced threshold)
   • Medical AI: Optimize for clinical outcome
   • Sepsis early warning: Prioritize sensitivity (catch cases)
   • Diagnostic confirmation: Prioritize specificity (avoid false positives)
        """)


# Main execution
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    
    from data_ingestion_v2 import DataIngestionModule
    from feature_engineering import ClinicalFeatureEngineer
    from model_training import ImbalanceAwareModelTrainer
    
    # Load data
    print("Loading data...")
    possible_paths = [
        "icu-early-warning/Dataset.csv",
        "Dataset.csv",
        "../Dataset.csv",
    ]
    
    dataset_path = None
    for path in possible_paths:
        if os.path.exists(path):
            dataset_path = path
            break
    
    if dataset_path is None:
        raise FileNotFoundError("Dataset.csv not found")
    
    df = pd.read_csv(dataset_path)
    print(f"✓ Loaded {df.shape[0]} rows × {df.shape[1]} columns")
    
    # Sample for speed
    print("Sampling 2% for quick test...")
    df = df.sample(frac=0.02, random_state=42)
    
    # Engineer features
    print("Engineering features...")
    engineer = ClinicalFeatureEngineer(df)
    df_engineered, _ = engineer.run_feature_engineering()
    
    # Find target
    target_col = 'SepsisLabel'
    
    # Train model
    print("Training model...")
    trainer = ImbalanceAwareModelTrainer(df_engineered, target_col)
    trainer.prepare_data()
    trainer.train_weighted_model()
    
    # Get predictions
    y_pred_proba = trainer.model_weighted.predict_proba(trainer.X_test)[:, 1]
    
    # Calibration and threshold optimization
    print("\nInitializing calibration optimizer...")
    optimizer = CalibrationAndThresholdOptimizer(
        trainer.y_test.values, y_pred_proba, trainer.model_weighted
    )
    
    # Run full pipeline
    optimizer.evaluate_calibration()
    optimizer.apply_calibration(method='isotonic')
    optimizer.optimize_thresholds()
    clinical_thresholds = optimizer.identify_clinical_thresholds()
    
    # Print explanations
    optimizer.print_calibration_explanation()
    
    print("\n" + "=" * 80)
    print("✓ CALIBRATION AND THRESHOLD OPTIMIZATION COMPLETE")
    print("=" * 80)
    print("\nRecommended Clinical Thresholds:")
    print(f"  High-Sensitivity: {clinical_thresholds['high_sensitivity']['threshold']:.2f}")
    print(f"  Balanced: {clinical_thresholds['balanced']['threshold']:.2f}")
