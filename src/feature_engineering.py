"""
Clinical Feature Engineering Module
Transforms raw vitals/labs into physiologically meaningful risk predictors
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


class ClinicalFeatureEngineer:
    """Engineer clinically meaningful features from raw vital signs and labs."""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize feature engineer.
        
        Args:
            df: Raw dataframe from data ingestion
        """
        self.df = df.copy()  # Keep original intact
        self.original_columns = list(df.columns)
        self.new_features = []
        self.feature_explanations = {}
    
    def _find_column(self, keywords: List[str]) -> str:
        """
        Find column by keyword matching (case-insensitive).
        
        Args:
            keywords: List of possible column names/keywords
        
        Returns:
            Column name if found, None otherwise
        """
        cols_lower = {col.lower(): col for col in self.df.columns}
        for keyword in keywords:
            if keyword.lower() in cols_lower:
                return cols_lower[keyword.lower()]
        return None
    
    def create_shock_index(self) -> pd.DataFrame:
        """
        Create Shock Index = Heart Rate / Systolic Blood Pressure.
        
        Clinical Rationale:
        - Shock Index > 0.9 indicates potential shock/hemodynamic instability
        - Combines HR (sympathetic response) with SBP (perfusion pressure)
        - Early indicator of compensatory mechanisms failing
        - Used in trauma and sepsis protocols
        """
        print("\n[1/6] Creating Shock Index...")
        
        hr_col = self._find_column(['heart rate', 'hr', 'heart_rate'])
        sbp_col = self._find_column(['systolic', 'sbp', 'systolic_bp'])
        
        if hr_col and sbp_col:
            # Avoid division by zero
            self.df['shock_index'] = np.where(
                self.df[sbp_col] > 0,
                self.df[hr_col] / self.df[sbp_col],
                np.nan
            )
            self.new_features.append('shock_index')
            self.feature_explanations['shock_index'] = (
                "HR/SBP ratio. Values >0.9 suggest hemodynamic instability. "
                "Combines heart rate response with perfusion pressure."
            )
            print(f"✓ Shock Index created (HR/SBP)")
        else:
            print(f"⚠ Missing HR or SBP columns")
        
        return self.df
    
    def create_pulse_pressure(self) -> pd.DataFrame:
        """
        Create Pulse Pressure = SBP - DBP.
        
        Clinical Rationale:
        - Normal: 40-60 mmHg
        - Low pulse pressure (<30) indicates reduced cardiac output or increased vascular resistance
        - High pulse pressure (>60) may indicate stiffness or hyperdynamic state
        - Useful for assessing vascular compliance
        """
        print("[2/6] Creating Pulse Pressure...")
        
        sbp_col = self._find_column(['systolic', 'sbp', 'systolic_bp'])
        dbp_col = self._find_column(['diastolic', 'dbp', 'diastolic_bp'])
        
        if sbp_col and dbp_col:
            self.df['pulse_pressure'] = self.df[sbp_col] - self.df[dbp_col]
            self.new_features.append('pulse_pressure')
            self.feature_explanations['pulse_pressure'] = (
                "SBP - DBP. Normal 40-60 mmHg. Low values suggest reduced cardiac output. "
                "High values may indicate hyperdynamic state or arterial stiffness."
            )
            print(f"✓ Pulse Pressure created (SBP - DBP)")
        else:
            print(f"⚠ Missing SBP or DBP columns")
        
        return self.df
    
    def create_map(self) -> pd.DataFrame:
        """
        Create Mean Arterial Pressure (MAP) if not present.
        
        Formula: MAP = (SBP + 2*DBP) / 3
        
        Clinical Rationale:
        - MAP < 65 mmHg indicates inadequate tissue perfusion
        - Critical threshold for organ perfusion in sepsis protocols
        - More representative of perfusion than SBP alone
        """
        print("[3/6] Creating Mean Arterial Pressure (MAP)...")
        
        # Check if MAP already exists
        map_col = self._find_column(['map', 'mean_arterial', 'mean_arterial_pressure'])
        
        if map_col:
            print(f"✓ MAP already exists: {map_col}")
            return self.df
        
        sbp_col = self._find_column(['systolic', 'sbp', 'systolic_bp'])
        dbp_col = self._find_column(['diastolic', 'dbp', 'diastolic_bp'])
        
        if sbp_col and dbp_col:
            self.df['MAP'] = (self.df[sbp_col] + 2 * self.df[dbp_col]) / 3
            self.new_features.append('MAP')
            self.feature_explanations['MAP'] = (
                "Mean Arterial Pressure = (SBP + 2*DBP)/3. "
                "MAP < 65 mmHg indicates inadequate tissue perfusion. "
                "Critical threshold in sepsis management."
            )
            print(f"✓ MAP created: (SBP + 2*DBP)/3")
        else:
            print(f"⚠ Missing SBP or DBP columns")
        
        return self.df
    
    def create_instability_flags(self) -> pd.DataFrame:
        """
        Create binary flags for hemodynamic instability indicators.
        
        Flags:
        - high_hr: HR > 90th percentile (tachycardia)
        - low_sbp: SBP < 10th percentile (hypotension)
        - low_map: MAP < 65 mmHg (inadequate perfusion)
        - hypoxia: SpO2 < 90% (severe hypoxemia)
        """
        print("[4/6] Creating Instability Flags...")
        
        # High Heart Rate Flag (tachycardia)
        hr_col = self._find_column(['heart rate', 'hr', 'heart_rate'])
        if hr_col:
            hr_90th = self.df[hr_col].quantile(0.90)
            self.df['high_hr_flag'] = (self.df[hr_col] > hr_90th).astype(int)
            self.new_features.append('high_hr_flag')
            self.feature_explanations['high_hr_flag'] = (
                f"Binary flag: HR > {hr_90th:.0f} bpm (90th percentile). "
                "Indicates tachycardia, common in sepsis and shock."
            )
            print(f"✓ High HR flag created (threshold: {hr_90th:.0f} bpm)")
        
        # Low Systolic BP Flag (hypotension)
        sbp_col = self._find_column(['systolic', 'sbp', 'systolic_bp'])
        if sbp_col:
            sbp_10th = self.df[sbp_col].quantile(0.10)
            self.df['low_sbp_flag'] = (self.df[sbp_col] < sbp_10th).astype(int)
            self.new_features.append('low_sbp_flag')
            self.feature_explanations['low_sbp_flag'] = (
                f"Binary flag: SBP < {sbp_10th:.0f} mmHg (10th percentile). "
                "Indicates hypotension, critical in sepsis."
            )
            print(f"✓ Low SBP flag created (threshold: {sbp_10th:.0f} mmHg)")
        
        # Low MAP Flag (inadequate perfusion)
        if 'MAP' in self.df.columns:
            self.df['low_map_flag'] = (self.df['MAP'] < 65).astype(int)
            self.new_features.append('low_map_flag')
            self.feature_explanations['low_map_flag'] = (
                "Binary flag: MAP < 65 mmHg. "
                "Indicates inadequate tissue perfusion. Critical threshold in sepsis protocols."
            )
            print(f"✓ Low MAP flag created (threshold: 65 mmHg)")
        
        # Hypoxia Flag (low oxygen saturation)
        spo2_col = self._find_column(['spo2', 'oxygen', 'o2_sat', 'oxygen_saturation'])
        if spo2_col:
            self.df['hypoxia_flag'] = (self.df[spo2_col] < 90).astype(int)
            self.new_features.append('hypoxia_flag')
            self.feature_explanations['hypoxia_flag'] = (
                "Binary flag: SpO2 < 90%. "
                "Indicates severe hypoxemia, associated with organ dysfunction."
            )
            print(f"✓ Hypoxia flag created (threshold: 90%)")
        
        return self.df
    
    def create_consistency_checks(self) -> pd.DataFrame:
        """
        Create features checking consistency between related vitals.
        
        Example: Absolute difference between SBP and MAP
        - Should be consistent with DBP
        - Large discrepancies may indicate measurement error or physiologic abnormality
        """
        print("[5/6] Creating Consistency Check Features...")
        
        sbp_col = self._find_column(['systolic', 'sbp', 'systolic_bp'])
        dbp_col = self._find_column(['diastolic', 'dbp', 'diastolic_bp'])
        
        if sbp_col and dbp_col and 'MAP' in self.df.columns:
            # Expected MAP from SBP/DBP
            expected_map = (self.df[sbp_col] + 2 * self.df[dbp_col]) / 3
            
            # Absolute difference (should be near zero if measurements are consistent)
            self.df['map_consistency_error'] = np.abs(self.df['MAP'] - expected_map)
            self.new_features.append('map_consistency_error')
            self.feature_explanations['map_consistency_error'] = (
                "Absolute difference between measured MAP and calculated MAP. "
                "Large values may indicate measurement error or physiologic abnormality."
            )
            print(f"✓ MAP consistency check created")
        
        return self.df
    
    def create_missingness_indicators(self) -> pd.DataFrame:
        """
        Create binary columns indicating missing values.
        
        Clinical Rationale:
        - Missing vital signs may indicate monitoring gaps
        - Pattern of missing data can be informative (e.g., missing lactate in non-sepsis)
        - Helps model account for incomplete monitoring
        """
        print("[6/6] Creating Missingness Indicators...")
        
        # Identify columns with any missing values
        cols_with_missing = self.df.columns[self.df.isnull().any()].tolist()
        
        for col in cols_with_missing:
            # Skip if already a missingness indicator
            if 'missing' in col.lower() or 'flag' in col.lower():
                continue
            
            missing_col_name = f'{col}_missing'
            self.df[missing_col_name] = self.df[col].isnull().astype(int)
            self.new_features.append(missing_col_name)
            self.feature_explanations[missing_col_name] = (
                f"Binary indicator: 1 if {col} is missing, 0 otherwise. "
                "Captures monitoring gaps and data availability patterns."
            )
        
        if cols_with_missing:
            print(f"✓ Created {len(cols_with_missing)} missingness indicators")
        else:
            print(f"✓ No missing values detected")
        
        return self.df
    
    def generate_feature_report(self) -> Dict:
        """
        Generate comprehensive feature engineering report.
        
        Returns:
            Dict with feature statistics and explanations
        """
        report = {
            'original_features': len(self.original_columns),
            'new_features': len(self.new_features),
            'total_features': len(self.df.columns),
            'new_feature_names': self.new_features,
            'feature_explanations': self.feature_explanations,
        }
        
        return report
    
    def run_feature_engineering(self) -> Tuple[pd.DataFrame, Dict]:
        """
        Execute full feature engineering pipeline.
        
        Returns:
            (engineered_dataframe, report)
        """
        print("\n" + "=" * 80)
        print("CLINICAL FEATURE ENGINEERING")
        print("=" * 80)
        
        # Create derived indices
        self.create_shock_index()
        self.create_pulse_pressure()
        self.create_map()
        
        # Create instability flags
        self.create_instability_flags()
        
        # Create consistency checks
        self.create_consistency_checks()
        
        # Create missingness indicators
        self.create_missingness_indicators()
        
        # Generate report
        report = self.generate_feature_report()
        
        # Print summary
        print("\n" + "=" * 80)
        print("FEATURE ENGINEERING SUMMARY")
        print("=" * 80)
        print(f"\nOriginal Features: {report['original_features']}")
        print(f"New Features Created: {report['new_features']}")
        print(f"Total Features: {report['total_features']}")
        
        print(f"\nNew Features:")
        for feat in report['new_feature_names']:
            print(f"  • {feat}")
            if feat in report['feature_explanations']:
                print(f"    → {report['feature_explanations'][feat]}")
        
        print("\n" + "=" * 80)
        print("✓ FEATURE ENGINEERING COMPLETE")
        print("=" * 80 + "\n")
        
        return self.df, report


# Main execution
if __name__ == "__main__":
    import sys
    import os
    
    # Add current directory to path
    sys.path.insert(0, os.path.dirname(__file__))
    
    from data_ingestion_v2 import DataIngestionModule
    
    # Load data
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
    
    ingestion = DataIngestionModule(dataset_path)
    df, _ = ingestion.run_validation()
    
    # Engineer features
    engineer = ClinicalFeatureEngineer(df)
    df_engineered, report = engineer.run_feature_engineering()
    
    # Display sample
    print("\nSample of engineered features:")
    print(df_engineered[report['new_feature_names']].head(10))
    
    print("\n✓ Ready for model training!")
