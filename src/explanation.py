"""
Clinical Interpretability Module
Makes model predictions transparent and clinically explainable
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class ClinicalExplainer:
    """Explains model predictions in clinically meaningful terms."""
    
    def __init__(self, model, X_train: pd.DataFrame, X_test: pd.DataFrame, 
                 y_test: pd.Series, feature_names: List[str] = None):
        """
        Initialize explainer.
        
        Args:
            model: Trained logistic regression model
            X_train: Training features
            X_test: Test features
            y_test: Test labels
            feature_names: List of feature names
        """
        self.model = model
        self.X_train = X_train
        self.X_test = X_test
        self.y_test = y_test
        self.feature_names = feature_names or X_test.columns.tolist()
        
        self.global_importance = None
        self.clinical_features_map = self._create_clinical_features_map()
    
    def _create_clinical_features_map(self) -> Dict:
        """Map features to clinical interpretations."""
        return {
            # Vital signs
            'HR': {'category': 'Vital Signs', 'unit': 'bpm', 'normal_range': '60-100'},
            'SBP': {'category': 'Vital Signs', 'unit': 'mmHg', 'normal_range': '90-140'},
            'DBP': {'category': 'Vital Signs', 'unit': 'mmHg', 'normal_range': '60-90'},
            'MAP': {'category': 'Vital Signs', 'unit': 'mmHg', 'normal_range': '>65'},
            'Resp': {'category': 'Vital Signs', 'unit': 'breaths/min', 'normal_range': '12-20'},
            'Temp': {'category': 'Vital Signs', 'unit': '°C', 'normal_range': '36.5-37.5'},
            'O2Sat': {'category': 'Vital Signs', 'unit': '%', 'normal_range': '>95'},
            
            # Derived indices
            'shock_index': {'category': 'Hemodynamic Index', 'unit': 'ratio', 'normal_range': '<0.9'},
            'pulse_pressure': {'category': 'Hemodynamic Index', 'unit': 'mmHg', 'normal_range': '40-60'},
            'map_consistency_error': {'category': 'Data Quality', 'unit': 'mmHg', 'normal_range': '<5'},
            
            # Flags
            'high_hr_flag': {'category': 'Risk Flag', 'unit': 'binary', 'meaning': 'Tachycardia'},
            'low_sbp_flag': {'category': 'Risk Flag', 'unit': 'binary', 'meaning': 'Hypotension'},
            'low_map_flag': {'category': 'Risk Flag', 'unit': 'binary', 'meaning': 'Inadequate perfusion'},
            
            # Labs
            'WBC': {'category': 'Laboratory', 'unit': 'K/µL', 'normal_range': '4.5-11'},
            'Lactate': {'category': 'Laboratory', 'unit': 'mmol/L', 'normal_range': '<2'},
            'Glucose': {'category': 'Laboratory', 'unit': 'mg/dL', 'normal_range': '70-100'},
            'Creatinine': {'category': 'Laboratory', 'unit': 'mg/dL', 'normal_range': '0.7-1.3'},
            'BUN': {'category': 'Laboratory', 'unit': 'mg/dL', 'normal_range': '7-20'},
            'pH': {'category': 'Laboratory', 'unit': 'pH', 'normal_range': '7.35-7.45'},
            'Potassium': {'category': 'Laboratory', 'unit': 'mEq/L', 'normal_range': '3.5-5.0'},
            'Chloride': {'category': 'Laboratory', 'unit': 'mEq/L', 'normal_range': '96-106'},
            'Calcium': {'category': 'Laboratory', 'unit': 'mg/dL', 'normal_range': '8.5-10.5'},
            'Magnesium': {'category': 'Laboratory', 'unit': 'mg/dL', 'normal_range': '1.7-2.2'},
            'Phosphate': {'category': 'Laboratory', 'unit': 'mg/dL', 'normal_range': '2.5-4.5'},
            'Platelets': {'category': 'Laboratory', 'unit': 'K/µL', 'normal_range': '150-400'},
            'Hgb': {'category': 'Laboratory', 'unit': 'g/dL', 'normal_range': '12-16'},
            'Hct': {'category': 'Laboratory', 'unit': '%', 'normal_range': '36-46'},
            
            # Demographics
            'Age': {'category': 'Demographics', 'unit': 'years', 'normal_range': 'N/A'},
            'Gender': {'category': 'Demographics', 'unit': 'binary', 'normal_range': 'N/A'},
        }
    
    def extract_global_importance(self) -> pd.DataFrame:
        """
        Extract feature importance from logistic regression coefficients.
        
        Returns:
            DataFrame with feature importance rankings
        """
        print("\n" + "=" * 80)
        print("STEP 1: GLOBAL FEATURE IMPORTANCE")
        print("=" * 80)
        
        # Get coefficients
        coefficients = self.model.coef_[0]
        
        # Create importance dataframe
        importance_df = pd.DataFrame({
            'Feature': self.feature_names,
            'Coefficient': coefficients,
            'Abs_Coefficient': np.abs(coefficients)
        })
        
        # Sort by absolute coefficient
        importance_df = importance_df.sort_values('Abs_Coefficient', ascending=False)
        importance_df['Rank'] = range(1, len(importance_df) + 1)
        importance_df['Direction'] = importance_df['Coefficient'].apply(
            lambda x: '↑ Increases Risk' if x > 0 else '↓ Decreases Risk'
        )
        
        self.global_importance = importance_df
        
        # Display top 10
        print("\nTop 10 Most Influential Features:")
        print("-" * 80)
        top_10 = importance_df.head(10)
        
        for idx, row in top_10.iterrows():
            feature_name = row['Feature']
            coef = row['Coefficient']
            direction = row['Direction']
            
            # Get clinical info
            clinical_info = self.clinical_features_map.get(
                feature_name, {'category': 'Other', 'unit': 'N/A'}
            )
            category = clinical_info.get('category', 'Other')
            
            print(f"\n{row['Rank']}. {feature_name} ({category})")
            print(f"   Coefficient: {coef:.4f}")
            print(f"   {direction}")
            print(f"   Interpretation: ", end="")
            
            if coef > 0:
                print(f"Higher {feature_name} → Higher sepsis risk")
            else:
                print(f"Higher {feature_name} → Lower sepsis risk")
        
        return importance_df
    
    def explain_patient_prediction(self, patient_idx: int, 
                                   y_pred_proba: np.ndarray) -> Dict:
        """
        Explain prediction for a specific patient.
        
        Args:
            patient_idx: Index of patient in test set
            y_pred_proba: Predicted probabilities for test set
        
        Returns:
            Dictionary with patient explanation
        """
        print("\n" + "=" * 80)
        print("STEP 2: LOCAL PREDICTION EXPLANATION")
        print("=" * 80)
        
        # Get patient data
        patient_features = self.X_test.iloc[patient_idx]
        patient_proba = y_pred_proba[patient_idx]
        patient_label = self.y_test.iloc[patient_idx]
        
        # Get coefficients
        coefficients = self.model.coef_[0]
        intercept = self.model.intercept_[0]
        
        # Calculate contribution of each feature
        contributions = patient_features.values * coefficients
        
        # Create contribution dataframe
        contrib_df = pd.DataFrame({
            'Feature': self.feature_names,
            'Value': patient_features.values,
            'Coefficient': coefficients,
            'Contribution': contributions,
            'Abs_Contribution': np.abs(contributions)
        })
        
        # Sort by absolute contribution
        contrib_df = contrib_df.sort_values('Abs_Contribution', ascending=False)
        
        # Display patient info
        print(f"\nPatient #{patient_idx}")
        print(f"Predicted Sepsis Probability: {patient_proba:.1%}")
        print(f"Actual Label: {'Sepsis' if patient_label == 1 else 'No Sepsis'}")
        print(f"Prediction: {'✓ CORRECT' if (patient_proba > 0.5) == patient_label else '✗ INCORRECT'}")
        
        # Display top contributing features
        print(f"\nTop 5 Contributing Features:")
        print("-" * 80)
        
        top_contributors = contrib_df.head(5)
        
        for idx, row in top_contributors.iterrows():
            feature_name = row['Feature']
            value = row['Value']
            coef = row['Coefficient']
            contrib = row['Contribution']
            
            clinical_info = self.clinical_features_map.get(
                feature_name, {'category': 'Other', 'unit': 'N/A', 'normal_range': 'N/A'}
            )
            
            print(f"\n{feature_name}:")
            print(f"  Patient Value: {value:.2f} {clinical_info.get('unit', '')}")
            print(f"  Normal Range: {clinical_info.get('normal_range', 'N/A')}")
            print(f"  Contribution to Risk: {contrib:.4f}")
            
            if contrib > 0:
                print(f"  ↑ INCREASES sepsis risk")
            else:
                print(f"  ↓ DECREASES sepsis risk")
        
        return {
            'patient_idx': patient_idx,
            'predicted_probability': patient_proba,
            'actual_label': patient_label,
            'contributions': contrib_df,
            'top_contributors': top_contributors
        }
    
    def generate_clinical_narrative(self, patient_explanation: Dict) -> str:
        """
        Generate clinician-friendly narrative explanation.
        
        Args:
            patient_explanation: Output from explain_patient_prediction
        
        Returns:
            Clinical narrative string
        """
        print("\n" + "=" * 80)
        print("STEP 3: CLINICAL INTERPRETATION NARRATIVE")
        print("=" * 80)
        
        proba = patient_explanation['predicted_probability']
        top_contrib = patient_explanation['top_contributors']
        
        # Build narrative
        narrative = f"""
SEPSIS RISK ASSESSMENT REPORT
{'=' * 80}

RISK SUMMARY:
The model predicts a {proba:.1%} probability of sepsis for this patient.

RISK LEVEL:
"""
        
        if proba > 0.40:
            narrative += "🔴 HIGH RISK - Immediate clinical evaluation recommended\n"
        elif proba > 0.25:
            narrative += "🟡 MODERATE RISK - Close monitoring and evaluation recommended\n"
        else:
            narrative += "🟢 LOW RISK - Continue routine monitoring\n"
        
        narrative += f"""
KEY FINDINGS:
The following clinical features are most influential in this risk assessment:

"""
        
        # Add top contributors
        for idx, (_, row) in enumerate(top_contrib.iterrows(), 1):
            feature = row['Feature']
            value = row['Value']
            contrib = row['Contribution']
            
            clinical_info = self.clinical_features_map.get(
                feature, {'category': 'Other', 'unit': 'N/A', 'normal_range': 'N/A'}
            )
            
            unit = clinical_info.get('unit', '')
            normal = clinical_info.get('normal_range', 'N/A')
            
            narrative += f"{idx}. {feature}: {value:.2f} {unit}\n"
            narrative += f"   Normal Range: {normal}\n"
            
            if contrib > 0:
                narrative += f"   Status: ABNORMAL - Increases sepsis risk\n"
            else:
                narrative += f"   Status: NORMAL - Decreases sepsis risk\n"
            narrative += "\n"
        
        narrative += f"""
CLINICAL INTERPRETATION:
"""
        
        # Generate interpretation based on top features
        risk_factors = []
        protective_factors = []
        
        for _, row in top_contrib.head(3).iterrows():
            if row['Contribution'] > 0:
                risk_factors.append(row['Feature'])
            else:
                protective_factors.append(row['Feature'])
        
        if risk_factors:
            narrative += f"Risk-increasing factors: {', '.join(risk_factors)}\n"
        if protective_factors:
            narrative += f"Protective factors: {', '.join(protective_factors)}\n"
        
        narrative += f"""
RECOMMENDATION:
Based on the model's assessment and clinical context, consider:
- Continued close monitoring of vital signs and laboratory values
- Evaluation for sepsis criteria (SIRS, qSOFA, or SOFA score)
- Consideration of blood cultures and lactate measurement if not already done
- Empiric antibiotic therapy if clinical suspicion is high

DISCLAIMER:
This model is a clinical decision support tool and should not replace clinical judgment.
All recommendations should be integrated with comprehensive clinical assessment.
"""
        
        print(narrative)
        return narrative
    
    def plot_global_importance(self, top_n: int = 15, save_path: str = None):
        """Plot global feature importance."""
        if self.global_importance is None:
            print("⚠ Run extract_global_importance() first")
            return
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        top_features = self.global_importance.head(top_n)
        colors = ['#e74c3c' if x > 0 else '#27ae60' for x in top_features['Coefficient']]
        
        ax.barh(range(len(top_features)), top_features['Coefficient'], color=colors)
        ax.set_yticks(range(len(top_features)))
        ax.set_yticklabels(top_features['Feature'])
        ax.set_xlabel('Coefficient (Impact on Sepsis Risk)', fontweight='bold', fontsize=12)
        ax.set_title(f'Top {top_n} Most Influential Features\n(Red = Increases Risk, Green = Decreases Risk)', 
                     fontweight='bold', fontsize=14)
        ax.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
        ax.grid(True, alpha=0.3, axis='x')
        
        # Invert y-axis so top feature is at top
        ax.invert_yaxis()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Feature importance plot saved to {save_path}")
        
        return fig
    
    def plot_patient_contributions(self, patient_explanation: Dict, 
                                   save_path: str = None):
        """Plot patient-specific feature contributions."""
        contrib_df = patient_explanation['contributions'].head(10)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        colors = ['#e74c3c' if x > 0 else '#27ae60' for x in contrib_df['Contribution']]
        
        ax.barh(range(len(contrib_df)), contrib_df['Contribution'], color=colors)
        ax.set_yticks(range(len(contrib_df)))
        ax.set_yticklabels(contrib_df['Feature'])
        ax.set_xlabel('Contribution to Sepsis Risk', fontweight='bold', fontsize=12)
        ax.set_title('Top 10 Features Contributing to This Patient\'s Risk Score\n(Red = Increases Risk, Green = Decreases Risk)', 
                     fontweight='bold', fontsize=14)
        ax.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
        ax.grid(True, alpha=0.3, axis='x')
        
        ax.invert_yaxis()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Patient contribution plot saved to {save_path}")
        
        return fig
    
    def print_interpretability_guide(self):
        """Print guide on why interpretability matters."""
        print("\n" + "=" * 80)
        print("WHY INTERPRETABILITY IS CRITICAL IN CLINICAL AI")
        print("=" * 80)
        
        print("""
1. CLINICAL TRUST & ADOPTION
   ──────────────────────────
   • Clinicians need to understand WHY the model makes predictions
   • Black-box models are not trusted in clinical settings
   • Explainability builds confidence in AI recommendations
   • Clinicians can verify if predictions align with clinical knowledge
   
2. REGULATORY & COMPLIANCE
   ───────────────────────
   • FDA requires explainability for clinical AI devices
   • HIPAA requires transparency in automated decisions
   • Clinicians must be able to explain decisions to patients
   • Liability requires understanding model behavior
   
3. ERROR DETECTION & DEBUGGING
   ────────────────────────────
   • Identify when model relies on spurious correlations
   • Detect data quality issues (e.g., missing values)
   • Catch distribution shifts in new patient populations
   • Validate that model learns clinically meaningful patterns
   
4. CLINICAL VALIDATION
   ───────────────────
   • Verify model captures known sepsis risk factors
   • Ensure predictions align with clinical guidelines
   • Identify missing important features
   • Validate against clinical expertise
   
5. CONTINUOUS IMPROVEMENT
   ──────────────────────
   • Understand which features drive predictions
   • Identify opportunities for feature engineering
   • Prioritize data collection efforts
   • Guide model retraining and updates

PHYSIOLOGICAL INTERPRETATION OF TOP FEATURES:

Shock Index (HR/SBP):
• Combines heart rate and blood pressure into single metric
• High shock index (>0.9) indicates hemodynamic instability
• Strongly predictive of sepsis and shock
• Reflects body's compensatory response to infection

Pulse Pressure (SBP - DBP):
• Measures arterial compliance and vascular stiffness
• Low pulse pressure (<40 mmHg) suggests reduced cardiac output
• Associated with septic shock and poor perfusion
• Indicates vascular dysfunction

Heart Rate (HR):
• Tachycardia (>100 bpm) is SIRS criterion for sepsis
• Reflects sympathetic activation and metabolic stress
• Elevated HR common in early sepsis
• Prognostic indicator of severity

Blood Pressure (SBP/MAP):
• Hypotension (<90 mmHg SBP) indicates septic shock
• MAP <65 mmHg associated with inadequate tissue perfusion
• Critical threshold for organ dysfunction
• Requires immediate intervention

Lactate:
• Marker of tissue hypoperfusion and anaerobic metabolism
• Elevated lactate (>2 mmol/L) indicates sepsis severity
• Prognostic indicator of mortality
• Reflects microcirculatory dysfunction

White Blood Cell Count (WBC):
• Elevated WBC (>11 K/µL) indicates infection/inflammation
• SIRS criterion for sepsis
• Reflects immune system activation
• Can be normal or low in severe sepsis

Temperature:
• Fever (>38°C) or hypothermia (<36°C) are SIRS criteria
• Fever indicates infection/inflammation
• Hypothermia associated with worse prognosis
• Reflects systemic inflammatory response

Glucose:
• Hyperglycemia common in sepsis (stress response)
• Elevated glucose associated with worse outcomes
• Reflects metabolic derangement
• Prognostic indicator in critical illness

pH & Lactate (Acid-Base Status):
• Metabolic acidosis indicates tissue hypoperfusion
• Low pH + high lactate = severe sepsis
• Reflects severity of organ dysfunction
• Prognostic indicator of mortality

WHY THESE FEATURES MATTER:
The model learns to recognize the physiologic signature of sepsis:
1. Hemodynamic instability (shock index, blood pressure)
2. Metabolic derangement (lactate, glucose, pH)
3. Inflammatory response (WBC, temperature)
4. Organ dysfunction (creatinine, bilirubin)

This aligns with clinical understanding of sepsis pathophysiology.
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
    
    # Create explainer
    print("\nInitializing explainer...")
    explainer = ClinicalExplainer(
        trainer.model_weighted,
        trainer.X_train,
        trainer.X_test,
        trainer.y_test,
        trainer.X_test.columns.tolist()
    )
    
    # Run full pipeline
    explainer.extract_global_importance()
    
    # Find a high-risk patient
    high_risk_idx = np.argmax(y_pred_proba)
    patient_explanation = explainer.explain_patient_prediction(high_risk_idx, y_pred_proba)
    
    # Generate narrative
    narrative = explainer.generate_clinical_narrative(patient_explanation)
    
    # Print guide
    explainer.print_interpretability_guide()
    
    # Generate plots
    print("\nGenerating plots...")
    explainer.plot_global_importance(save_path='feature_importance.png')
    explainer.plot_patient_contributions(patient_explanation, save_path='patient_contributions.png')
    
    print("\n" + "=" * 80)
    print("✓ CLINICAL INTERPRETABILITY ANALYSIS COMPLETE")
    print("=" * 80)
