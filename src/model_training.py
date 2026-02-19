"""
Imbalance-Aware Model Training Module
Trains baseline and weighted logistic regression models for sepsis prediction
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    roc_auc_score, roc_curve, auc,
    precision_recall_curve, average_precision_score,
    confusion_matrix, classification_report,
    precision_score, recall_score, f1_score
)
from typing import Dict, Tuple


class ImbalanceAwareModelTrainer:
    """Train and evaluate models on imbalanced sepsis prediction data."""
    
    def __init__(self, df: pd.DataFrame, target_col: str, test_size: float = 0.2, random_state: int = 42):
        """
        Initialize model trainer.
        
        Args:
            df: Dataframe with features and target
            target_col: Name of target column
            test_size: Proportion for test set
            random_state: Random seed for reproducibility
        """
        self.df = df
        self.target_col = target_col
        self.test_size = test_size
        self.random_state = random_state
        
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        
        self.model_baseline = None
        self.model_weighted = None
        
        self.results = {}
    
    def prepare_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """
        Split data into train/test with stratification.
        
        Stratification preserves class imbalance in both splits.
        This is critical for imbalanced datasets to ensure representative evaluation.
        
        Returns:
            (X_train, X_test, y_train, y_test)
        """
        print("\n" + "=" * 80)
        print("DATA PREPARATION")
        print("=" * 80)
        
        # Separate features and target
        X = self.df.drop(columns=[self.target_col])
        y = self.df[self.target_col]
        
        # Remove rows with NaN in target
        valid_idx = y.notna()
        X = X[valid_idx]
        y = y[valid_idx]
        
        # Drop columns that are entirely NaN
        X = X.dropna(axis=1, how='all')
        
        print(f"\nDataset shape: {X.shape}")
        print(f"Target distribution:")
        print(f"  Negative (0): {(y == 0).sum()} ({(y == 0).sum() / len(y) * 100:.2f}%)")
        print(f"  Positive (1): {(y == 1).sum()} ({(y == 1).sum() / len(y) * 100:.2f}%)")
        print(f"  Imbalance ratio: {(y == 0).sum() / (y == 1).sum():.1f}:1")
        
        # Fill NaN in features with median for all columns
        for col in X.columns:
            if X[col].isnull().any():
                X[col] = X[col].fillna(X[col].median())
        
        # Stratified train/test split
        print(f"\nSplitting data (80/20 with stratification)...")
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y,
            test_size=self.test_size,
            stratify=y,
            random_state=self.random_state
        )
        
        # Impute missing values using median strategy
        imputer = SimpleImputer(strategy='median')
        self.X_train = pd.DataFrame(
            imputer.fit_transform(self.X_train),
            columns=self.X_train.columns
        )
        self.X_test = pd.DataFrame(
            imputer.transform(self.X_test),
            columns=self.X_test.columns
        )
        
        print(f"Train set: {self.X_train.shape[0]} samples")
        print(f"  Negative: {(self.y_train == 0).sum()} ({(self.y_train == 0).sum() / len(self.y_train) * 100:.2f}%)")
        print(f"  Positive: {(self.y_train == 1).sum()} ({(self.y_train == 1).sum() / len(self.y_train) * 100:.2f}%)")
        
        print(f"\nTest set: {self.X_test.shape[0]} samples")
        print(f"  Negative: {(self.y_test == 0).sum()} ({(self.y_test == 0).sum() / len(self.y_test) * 100:.2f}%)")
        print(f"  Positive: {(self.y_test == 1).sum()} ({(self.y_test == 1).sum() / len(self.y_test) * 100:.2f}%)")
        
        return self.X_train, self.X_test, self.y_train, self.y_test
    
    def train_baseline_model(self) -> LogisticRegression:
        """
        Train baseline logistic regression (no class weighting).
        
        This model will be biased toward the majority class.
        Used as baseline to show importance of handling imbalance.
        """
        print("\n" + "=" * 80)
        print("MODEL A: BASELINE LOGISTIC REGRESSION (No Class Weighting)")
        print("=" * 80)
        
        print("\nTraining baseline model...")
        self.model_baseline = LogisticRegression(
            random_state=self.random_state,
            max_iter=1000,
            class_weight=None  # No weighting
        )
        self.model_baseline.fit(self.X_train, self.y_train)
        
        print("✓ Baseline model trained")
        
        return self.model_baseline
    
    def train_weighted_model(self) -> LogisticRegression:
        """
        Train logistic regression with balanced class weights.
        
        class_weight='balanced' automatically adjusts weights inversely proportional to class frequency.
        This penalizes misclassification of the minority class more heavily.
        """
        print("\n" + "=" * 80)
        print("MODEL B: WEIGHTED LOGISTIC REGRESSION (class_weight='balanced')")
        print("=" * 80)
        
        print("\nTraining weighted model...")
        self.model_weighted = LogisticRegression(
            random_state=self.random_state,
            max_iter=1000,
            class_weight='balanced'  # Automatic weight balancing
        )
        self.model_weighted.fit(self.X_train, self.y_train)
        
        print("✓ Weighted model trained")
        
        return self.model_weighted
    
    def evaluate_model(self, model: LogisticRegression, model_name: str) -> Dict:
        """
        Evaluate model on test set.
        
        Metrics:
        - AUROC: Overall discrimination ability
        - PR-AUC: Precision-Recall curve (better for imbalanced data)
        - Precision: Of predicted positives, how many are correct
        - Recall: Of actual positives, how many are detected
        - F1: Harmonic mean of precision and recall
        """
        print(f"\nEvaluating {model_name}...")
        
        # Predictions
        y_pred = model.predict(self.X_test)
        y_pred_proba = model.predict_proba(self.X_test)[:, 1]
        
        # Metrics
        auroc = roc_auc_score(self.y_test, y_pred_proba)
        pr_auc = average_precision_score(self.y_test, y_pred_proba)
        precision = precision_score(self.y_test, y_pred)
        recall = recall_score(self.y_test, y_pred)
        f1 = f1_score(self.y_test, y_pred)
        
        # Confusion matrix
        cm = confusion_matrix(self.y_test, y_pred)
        tn, fp, fn, tp = cm.ravel()
        
        results = {
            'model_name': model_name,
            'auroc': auroc,
            'pr_auc': pr_auc,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'confusion_matrix': cm,
            'y_pred': y_pred,
            'y_pred_proba': y_pred_proba,
            'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn
        }
        
        print(f"  AUROC: {auroc:.4f}")
        print(f"  PR-AUC: {pr_auc:.4f}")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall: {recall:.4f}")
        print(f"  F1 Score: {f1:.4f}")
        
        return results
    
    def print_comparison_table(self):
        """Print side-by-side comparison of baseline vs weighted model."""
        print("\n" + "=" * 80)
        print("MODEL COMPARISON: BASELINE vs WEIGHTED")
        print("=" * 80)
        
        baseline = self.results['baseline']
        weighted = self.results['weighted']
        
        comparison_data = {
            'Metric': ['AUROC', 'PR-AUC', 'Precision', 'Recall', 'F1 Score'],
            'Baseline': [
                f"{baseline['auroc']:.4f}",
                f"{baseline['pr_auc']:.4f}",
                f"{baseline['precision']:.4f}",
                f"{baseline['recall']:.4f}",
                f"{baseline['f1']:.4f}"
            ],
            'Weighted': [
                f"{weighted['auroc']:.4f}",
                f"{weighted['pr_auc']:.4f}",
                f"{weighted['precision']:.4f}",
                f"{weighted['recall']:.4f}",
                f"{weighted['f1']:.4f}"
            ],
            'Improvement': [
                f"{(weighted['auroc'] - baseline['auroc']):.4f}",
                f"{(weighted['pr_auc'] - baseline['pr_auc']):.4f}",
                f"{(weighted['precision'] - baseline['precision']):.4f}",
                f"{(weighted['recall'] - baseline['recall']):.4f}",
                f"{(weighted['f1'] - baseline['f1']):.4f}"
            ]
        }
        
        comparison_df = pd.DataFrame(comparison_data)
        print("\n" + comparison_df.to_string(index=False))
        
        print("\n" + "=" * 80)
        print("KEY INSIGHTS")
        print("=" * 80)
        print(f"\n✓ Recall Improvement: {(weighted['recall'] - baseline['recall']):.4f}")
        print(f"  → Weighted model detects {weighted['recall']*100:.1f}% of sepsis cases vs {baseline['recall']*100:.1f}%")
        
        print(f"\n✓ PR-AUC Improvement: {(weighted['pr_auc'] - baseline['pr_auc']):.4f}")
        print(f"  → Better at handling class imbalance (more relevant than AUROC)")
        
        print(f"\n⚠ Precision Trade-off: {(weighted['precision'] - baseline['precision']):.4f}")
        print(f"  → Weighted model has {weighted['precision']*100:.1f}% precision vs {baseline['precision']*100:.1f}%")
        print(f"  → More false positives, but better at catching sepsis cases")
    
    def print_classification_reports(self):
        """Print detailed classification reports."""
        print("\n" + "=" * 80)
        print("CLASSIFICATION REPORTS")
        print("=" * 80)
        
        print("\nBASELINE MODEL:")
        print(classification_report(self.y_test, self.results['baseline']['y_pred']))
        
        print("\nWEIGHTED MODEL:")
        print(classification_report(self.y_test, self.results['weighted']['y_pred']))
    
    def plot_roc_curves(self, save_path: str = None):
        """Plot ROC curves for both models."""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        for model_key, model_name in [('baseline', 'Baseline'), ('weighted', 'Weighted')]:
            results = self.results[model_key]
            fpr, tpr, _ = roc_curve(self.y_test, results['y_pred_proba'])
            roc_auc = results['auroc']
            
            ax.plot(fpr, tpr, label=f'{model_name} (AUROC = {roc_auc:.4f})', linewidth=2)
        
        ax.plot([0, 1], [0, 1], 'k--', label='Random Classifier', linewidth=1)
        ax.set_xlabel('False Positive Rate', fontweight='bold')
        ax.set_ylabel('True Positive Rate', fontweight='bold')
        ax.set_title('ROC Curves: Baseline vs Weighted Model', fontweight='bold')
        ax.legend(loc='lower right')
        ax.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_pr_curves(self, save_path: str = None):
        """Plot Precision-Recall curves for both models."""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        for model_key, model_name in [('baseline', 'Baseline'), ('weighted', 'Weighted')]:
            results = self.results[model_key]
            precision, recall, _ = precision_recall_curve(self.y_test, results['y_pred_proba'])
            pr_auc = results['pr_auc']
            
            ax.plot(recall, precision, label=f'{model_name} (PR-AUC = {pr_auc:.4f})', linewidth=2)
        
        ax.set_xlabel('Recall (Sensitivity)', fontweight='bold')
        ax.set_ylabel('Precision', fontweight='bold')
        ax.set_title('Precision-Recall Curves: Baseline vs Weighted Model', fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0, 1])
        ax.set_ylim([0, 1])
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def run_training_pipeline(self) -> Dict:
        """Execute full training and evaluation pipeline."""
        print("\n" + "=" * 80)
        print("IMBALANCE-AWARE MODEL TRAINING PIPELINE")
        print("=" * 80)
        
        # Prepare data
        self.prepare_data()
        
        # Train models
        self.train_baseline_model()
        self.train_weighted_model()
        
        # Evaluate models
        print("\n" + "=" * 80)
        print("MODEL EVALUATION")
        print("=" * 80)
        
        self.results['baseline'] = self.evaluate_model(self.model_baseline, "Baseline Model")
        self.results['weighted'] = self.evaluate_model(self.model_weighted, "Weighted Model")
        
        # Print comparison
        self.print_comparison_table()
        
        # Print classification reports
        self.print_classification_reports()
        
        # Print explanations
        self.print_explanations()
        
        return self.results
    
    def print_explanations(self):
        """Print explanations about metrics and imbalance handling."""
        print("\n" + "=" * 80)
        print("WHY THESE METRICS MATTER FOR IMBALANCED DATA")
        print("=" * 80)
        
        print("""
1. ACCURACY IS MISLEADING FOR IMBALANCED DATA
   ────────────────────────────────────────────
   • With 98% negative cases, a model predicting all negatives gets 98% accuracy
   • But it catches 0% of sepsis cases (useless clinically!)
   • Accuracy doesn't reflect minority class performance
   
2. PR-AUC IS MORE IMPORTANT THAN AUROC
   ────────────────────────────────────
   • AUROC: Measures discrimination across all thresholds
     - Can be misleading with severe imbalance
     - Dominated by majority class performance
   
   • PR-AUC: Precision-Recall curve
     - Focuses on minority class (sepsis cases)
     - More informative for rare-event detection
     - Better reflects clinical utility
   
3. RECALL (SENSITIVITY) IS CRITICAL
   ─────────────────────────────────
   • Recall = TP / (TP + FN)
   • "Of all sepsis cases, how many do we catch?"
   • Missing sepsis cases (FN) is clinically dangerous
   • Weighted model prioritizes catching sepsis
   
4. PRECISION-RECALL TRADE-OFF
   ──────────────────────────
   • Weighted model: Higher recall, lower precision
   • More false alarms, but fewer missed cases
   • Clinically acceptable for early warning system
   • Better to alert on non-sepsis than miss sepsis
        """)


# Main execution
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    
    from data_ingestion_v2 import DataIngestionModule
    from feature_engineering import ClinicalFeatureEngineer
    
    # Load and prepare data
    print("Loading data...")
    # Try multiple paths
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
        raise FileNotFoundError("Dataset.csv not found in any expected location")
    
    # Load data directly without verbose ingestion
    print(f"Loading from {dataset_path}...")
    df = pd.read_csv(dataset_path)
    print(f"✓ Loaded {df.shape[0]} rows × {df.shape[1]} columns")
    
    # Sample data for faster training (use 5% for demo)
    print("Sampling 5% of data for faster training...")
    df = df.sample(frac=0.05, random_state=42)
    print(f"✓ Sampled dataset shape: {df.shape}")
    
    # Engineer features
    print("\nEngineering features...")
    engineer = ClinicalFeatureEngineer(df)
    df_engineered, _ = engineer.run_feature_engineering()
    
    # Find target column
    target_col = None
    for col in df_engineered.columns:
        if 'sepsis' in col.lower():
            target_col = col
            break
    
    if target_col is None:
        print("⚠ No sepsis target column found")
        sys.exit(1)
    
    # Train models
    trainer = ImbalanceAwareModelTrainer(df_engineered, target_col)
    results = trainer.run_training_pipeline()
    
    print("\n✓ Model training complete!")
