"""
Improved Model Training - Ensemble Methods & Advanced Features
Combines multiple models for better accuracy
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score, average_precision_score
import xgboost as xgb
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import warnings
warnings.filterwarnings('ignore')


class ImprovedModelTrainer:
    """Train ensemble of models with advanced features."""
    
    def __init__(self, df: pd.DataFrame, target_col: str, test_size: float = 0.2, random_state: int = 42):
        """Initialize improved trainer."""
        self.df = df
        self.target_col = target_col
        self.test_size = test_size
        self.random_state = random_state
        
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        
        self.models = {}
        self.results = {}
        self.feature_names = None
        
    def create_advanced_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create advanced clinical features."""
        print("\n" + "=" * 80)
        print("CREATING ADVANCED FEATURES")
        print("=" * 80)
        
        df = df.copy()
        original_cols = len(df.columns)
        
        # 1. Interaction Terms
        if 'shock_index' in df.columns and 'Lactate' in df.columns:
            df['shock_index_lactate'] = df['shock_index'] * df['Lactate']
            print("✓ Created: shock_index_lactate")
        
        if 'MAP' in df.columns and 'Lactate' in df.columns:
            df['bp_lactate_ratio'] = df['MAP'] / (df['Lactate'] + 0.1)
            print("✓ Created: bp_lactate_ratio")
        
        if 'HR' in df.columns and 'SBP' in df.columns:
            df['hr_sbp_interaction'] = df['HR'] * df['SBP']
            print("✓ Created: hr_sbp_interaction")
        
        # 2. Clinical Severity Scores
        # SIRS Score (Systemic Inflammatory Response Syndrome)
        sirs_score = 0
        if 'Temp' in df.columns:
            sirs_score += (df['Temp'] > 38).astype(int)
        if 'HR' in df.columns:
            sirs_score += (df['HR'] > 100).astype(int)
        if 'Resp' in df.columns:
            sirs_score += (df['Resp'] > 20).astype(int)
        if 'WBC' in df.columns:
            sirs_score += (df['WBC'] > 12).astype(int)
        
        df['SIRS_score'] = sirs_score
        print("✓ Created: SIRS_score (0-4)")
        
        # 3. Metabolic Dysfunction Score
        metabolic_score = 0
        if 'Lactate' in df.columns:
            metabolic_score += (df['Lactate'] > 2).astype(int)
        if 'pH' in df.columns:
            metabolic_score += (df['pH'] < 7.35).astype(int)
        if 'Glucose' in df.columns:
            metabolic_score += (df['Glucose'] > 150).astype(int)
        
        df['metabolic_dysfunction'] = metabolic_score
        print("✓ Created: metabolic_dysfunction (0-3)")
        
        # 4. Hemodynamic Instability Score
        hemodynamic_score = 0
        if 'shock_index' in df.columns:
            hemodynamic_score += (df['shock_index'] > 0.9).astype(int)
        if 'MAP' in df.columns:
            hemodynamic_score += (df['MAP'] < 65).astype(int)
        if 'SBP' in df.columns:
            hemodynamic_score += (df['SBP'] < 90).astype(int)
        
        df['hemodynamic_instability'] = hemodynamic_score
        print("✓ Created: hemodynamic_instability (0-3)")
        
        # 5. Organ Dysfunction Indicators
        if 'Creatinine' in df.columns:
            df['acute_kidney_injury'] = (df['Creatinine'] > 1.5).astype(int)
            print("✓ Created: acute_kidney_injury")
        
        if 'Bilirubin' in df.columns:
            df['liver_dysfunction'] = (df['Bilirubin'] > 2).astype(int)
            print("✓ Created: liver_dysfunction")
        
        # 6. Polynomial Features (for non-linear relationships)
        if 'Lactate' in df.columns:
            df['Lactate_squared'] = df['Lactate'] ** 2
            print("✓ Created: Lactate_squared")
        
        if 'HR' in df.columns:
            df['HR_squared'] = df['HR'] ** 2
            print("✓ Created: HR_squared")
        
        # 7. Ratio Features
        if 'WBC' in df.columns and 'Platelets' in df.columns:
            df['wbc_platelet_ratio'] = df['WBC'] / (df['Platelets'] + 1)
            print("✓ Created: wbc_platelet_ratio")
        
        if 'Lactate' in df.columns and 'pH' in df.columns:
            df['lactate_ph_ratio'] = df['Lactate'] / (8 - df['pH'] + 0.1)
            print("✓ Created: lactate_ph_ratio")
        
        new_cols = len(df.columns)
        print(f"\n✓ Total new features created: {new_cols - original_cols}")
        print(f"✓ Total features now: {new_cols}")
        
        return df
    
    def prepare_data(self):
        """Prepare data with advanced features."""
        print("\n" + "=" * 80)
        print("PREPARING DATA WITH ADVANCED FEATURES")
        print("=" * 80)
        
        # Create advanced features
        df_enhanced = self.create_advanced_features(self.df)
        
        # Separate features and target
        X = df_enhanced.drop(columns=[self.target_col])
        y = df_enhanced[self.target_col]
        
        # Drop rows with NaN in target
        valid_idx = ~y.isna()
        X = X[valid_idx]
        y = y[valid_idx]
        
        # Handle categorical columns
        categorical_cols = X.select_dtypes(include=['object']).columns.tolist()
        if categorical_cols:
            print(f"\nEncoding {len(categorical_cols)} categorical columns...")
            from sklearn.preprocessing import LabelEncoder
            for col in categorical_cols:
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col].astype(str))
        
        # Handle missing values - drop rows with any NaN
        print(f"Rows before NaN removal: {len(X)}")
        X = X.dropna()
        y = y[X.index]
        print(f"Rows after NaN removal: {len(X)}")
        
        # Stratified split
        from sklearn.model_selection import train_test_split
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=self.test_size, stratify=y, random_state=self.random_state
        )
        
        self.feature_names = X.columns.tolist()
        
        print(f"\n✓ Training set: {len(self.X_train)} samples")
        print(f"✓ Test set: {len(self.X_test)} samples")
        print(f"✓ Features: {len(self.feature_names)}")
        print(f"✓ Class distribution (train): {self.y_train.value_counts().to_dict()}")
        
        return self.X_train, self.X_test, self.y_train, self.y_test
    
    def train_ensemble(self):
        """Train ensemble of models."""
        print("\n" + "=" * 80)
        print("TRAINING ENSEMBLE MODELS")
        print("=" * 80)
        
        # Prepare data
        self.prepare_data()
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(self.X_train)
        X_test_scaled = scaler.transform(self.X_test)
        
        # 1. Logistic Regression with SMOTE
        print("\n1. Training Logistic Regression with SMOTE...")
        lr_pipeline = ImbPipeline([
            ('smote', SMOTE(random_state=self.random_state)),
            ('lr', LogisticRegression(class_weight='balanced', max_iter=1000, random_state=self.random_state))
        ])
        lr_pipeline.fit(X_train_scaled, self.y_train)
        self.models['logistic_regression'] = lr_pipeline
        print("   ✓ Complete")
        
        # 2. Random Forest
        print("2. Training Random Forest...")
        rf = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            class_weight='balanced',
            random_state=self.random_state,
            n_jobs=-1
        )
        rf.fit(self.X_train, self.y_train)
        self.models['random_forest'] = rf
        print("   ✓ Complete")
        
        # 3. Gradient Boosting
        print("3. Training Gradient Boosting...")
        gb = GradientBoostingClassifier(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.1,
            random_state=self.random_state
        )
        gb.fit(self.X_train, self.y_train)
        self.models['gradient_boosting'] = gb
        print("   ✓ Complete")
        
        # 4. XGBoost
        print("4. Training XGBoost...")
        xgb_model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            scale_pos_weight=45,  # Handle class imbalance
            random_state=self.random_state,
            n_jobs=-1
        )
        xgb_model.fit(self.X_train, self.y_train)
        self.models['xgboost'] = xgb_model
        print("   ✓ Complete")
        
        print("\n✓ All models trained successfully!")
        
        return self.models
    
    def evaluate_ensemble(self):
        """Evaluate ensemble predictions."""
        print("\n" + "=" * 80)
        print("EVALUATING ENSEMBLE")
        print("=" * 80)
        
        # Get predictions from each model
        predictions = {}
        
        # Scale for logistic regression
        scaler = StandardScaler()
        X_test_scaled = scaler.fit_transform(self.X_train)
        X_test_scaled = scaler.transform(self.X_test)
        
        for name, model in self.models.items():
            if name == 'logistic_regression':
                pred_proba = model.predict_proba(X_test_scaled)[:, 1]
            else:
                pred_proba = model.predict_proba(self.X_test)[:, 1]
            predictions[name] = pred_proba
        
        # Ensemble prediction (average)
        ensemble_proba = np.mean(list(predictions.values()), axis=0)
        
        # Evaluate each model
        print("\nIndividual Model Performance:")
        print("-" * 80)
        
        for name, pred_proba in predictions.items():
            auroc = roc_auc_score(self.y_test, pred_proba)
            pr_auc = average_precision_score(self.y_test, pred_proba)
            
            pred = (pred_proba > 0.5).astype(int)
            precision = precision_score(self.y_test, pred)
            recall = recall_score(self.y_test, pred)
            f1 = f1_score(self.y_test, pred)
            
            self.results[name] = {
                'auroc': auroc,
                'pr_auc': pr_auc,
                'precision': precision,
                'recall': recall,
                'f1': f1
            }
            
            print(f"\n{name.upper()}:")
            print(f"  AUROC: {auroc:.4f}")
            print(f"  PR-AUC: {pr_auc:.4f}")
            print(f"  Precision: {precision:.4f}")
            print(f"  Recall: {recall:.4f}")
            print(f"  F1 Score: {f1:.4f}")
        
        # Evaluate ensemble
        print("\n" + "=" * 80)
        print("ENSEMBLE PERFORMANCE (Average of all models):")
        print("=" * 80)
        
        ensemble_auroc = roc_auc_score(self.y_test, ensemble_proba)
        ensemble_pr_auc = average_precision_score(self.y_test, ensemble_proba)
        
        ensemble_pred = (ensemble_proba > 0.5).astype(int)
        ensemble_precision = precision_score(self.y_test, ensemble_pred)
        ensemble_recall = recall_score(self.y_test, ensemble_pred)
        ensemble_f1 = f1_score(self.y_test, ensemble_pred)
        
        self.results['ensemble'] = {
            'auroc': ensemble_auroc,
            'pr_auc': ensemble_pr_auc,
            'precision': ensemble_precision,
            'recall': ensemble_recall,
            'f1': ensemble_f1
        }
        
        print(f"\nAUROC: {ensemble_auroc:.4f}")
        print(f"PR-AUC: {ensemble_pr_auc:.4f}")
        print(f"Precision: {ensemble_precision:.4f}")
        print(f"Recall: {ensemble_recall:.4f}")
        print(f"F1 Score: {ensemble_f1:.4f}")
        
        return self.results
    
    def cross_validate(self):
        """Perform cross-validation."""
        print("\n" + "=" * 80)
        print("CROSS-VALIDATION (5-Fold Stratified)")
        print("=" * 80)
        
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=self.random_state)
        
        for name, model in self.models.items():
            print(f"\n{name.upper()}:")
            
            if name == 'logistic_regression':
                # For pipeline, use scaled data
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(self.X_train)
                scores = cross_val_score(model, X_scaled, self.y_train, cv=skf, scoring='roc_auc')
            else:
                scores = cross_val_score(model, self.X_train, self.y_train, cv=skf, scoring='roc_auc')
            
            print(f"  Fold scores: {[f'{s:.4f}' for s in scores]}")
            print(f"  Mean AUROC: {scores.mean():.4f} (+/- {scores.std():.4f})")
        
        return scores
    
    def print_summary(self):
        """Print summary comparison."""
        print("\n" + "=" * 80)
        print("MODEL COMPARISON SUMMARY")
        print("=" * 80)
        
        summary_df = pd.DataFrame(self.results).T
        summary_df = summary_df.round(4)
        
        print("\n" + summary_df.to_string())
        
        # Highlight best model
        best_auroc = summary_df['auroc'].idxmax()
        best_recall = summary_df['recall'].idxmax()
        best_f1 = summary_df['f1'].idxmax()
        
        print(f"\n✓ Best AUROC: {best_auroc} ({summary_df.loc[best_auroc, 'auroc']:.4f})")
        print(f"✓ Best Recall: {best_recall} ({summary_df.loc[best_recall, 'recall']:.4f})")
        print(f"✓ Best F1: {best_f1} ({summary_df.loc[best_f1, 'f1']:.4f})")


# Main execution
if __name__ == "__main__":
    import os
    
    # Load data
    possible_paths = [
        "Dataset.csv",
        "icu-early-warning/Dataset.csv",
        "../Dataset.csv",
    ]
    
    dataset_path = None
    for path in possible_paths:
        if os.path.exists(path):
            dataset_path = path
            break
    
    if dataset_path is None:
        print("⚠ Dataset.csv not found")
    else:
        print(f"Loading data from {dataset_path}...")
        df = pd.read_csv(dataset_path)
        
        # Identify target column
        target_col = None
        for col in df.columns:
            if 'sepsis' in col.lower() or 'target' in col.lower() or 'label' in col.lower():
                target_col = col
                break
        
        if target_col is None:
            print("⚠ Target column not found")
        else:
            # Train improved model
            trainer = ImprovedModelTrainer(df, target_col=target_col)
            trainer.train_ensemble()
            trainer.evaluate_ensemble()
            trainer.cross_validate()
            trainer.print_summary()
