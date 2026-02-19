"""
Data Ingestion & Validation Module - Simplified
Loads and validates sepsis prediction dataset
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple


class DataIngestionModule:
    """Load, validate, and analyze sepsis dataset."""
    
    def __init__(self, filepath: str):
        """Initialize with dataset path."""
        self.filepath = filepath
        self.df = None
        self.report = {}
    
    def load_data(self) -> pd.DataFrame:
        """Load CSV file."""
        print(f"Loading data from {self.filepath}...")
        self.df = pd.read_csv(self.filepath)
        print(f"✓ Data loaded successfully\n")
        return self.df
    
    def print_basic_info(self):
        """Print dataset shape and first rows."""
        print("=" * 80)
        print("DATASET BASIC INFO")
        print("=" * 80)
        print(f"\nDataset Shape: {self.df.shape[0]} rows × {self.df.shape[1]} columns")
        print(f"\nColumn Names:\n{list(self.df.columns)}")
        print(f"\nFirst 5 Rows:")
        print(self.df.head())
        print()
    
    def identify_columns(self) -> Dict:
        """Identify target, numeric, and categorical columns."""
        print("=" * 80)
        print("COLUMN IDENTIFICATION")
        print("=" * 80)
        
        # Identify target column (look for 'sepsis', 'target', 'label')
        target_col = None
        for col in self.df.columns:
            if 'sepsis' in col.lower() or 'target' in col.lower() or 'label' in col.lower():
                target_col = col
                break
        
        # Identify patient ID column
        patient_col = None
        for col in self.df.columns:
            if 'patient' in col.lower() or 'id' in col.lower():
                patient_col = col
                break
        
        # Separate numeric and categorical
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = self.df.select_dtypes(include=['object']).columns.tolist()
        
        print(f"\nTarget Column: {target_col}")
        print(f"Patient ID Column: {patient_col}")
        print(f"\nNumeric Features ({len(numeric_cols)}): {numeric_cols}")
        print(f"\nCategorical Features ({len(categorical_cols)}): {categorical_cols}")
        print()
        
        return {
            'target': target_col,
            'patient_id': patient_col,
            'numeric': numeric_cols,
            'categorical': categorical_cols
        }
    
    def check_missing_values(self) -> pd.DataFrame:
        """Check for missing values."""
        print("=" * 80)
        print("MISSING VALUES ANALYSIS")
        print("=" * 80)
        
        missing_data = pd.DataFrame({
            'Column': self.df.columns,
            'Missing_Count': self.df.isnull().sum(),
            'Missing_Percentage': (self.df.isnull().sum() / len(self.df) * 100).round(2)
        })
        
        missing_data = missing_data[missing_data['Missing_Count'] > 0].sort_values('Missing_Percentage', ascending=False)
        
        if len(missing_data) == 0:
            print("\n✓ No missing values found!")
        else:
            print(f"\nMissing Values Summary:")
            print(missing_data.to_string(index=False))
        
        print()
        return missing_data
    
    def check_duplicates(self):
        """Check for duplicate rows."""
        print("=" * 80)
        print("DUPLICATE ROWS ANALYSIS")
        print("=" * 80)
        
        duplicates = self.df.duplicated().sum()
        print(f"\nTotal Duplicate Rows: {duplicates}")
        
        if duplicates > 0:
            print(f"⚠ Warning: {duplicates} duplicate rows found ({duplicates/len(self.df)*100:.2f}%)")
        else:
            print("✓ No duplicate rows found")
        
        print()
    
    def check_target_distribution(self, target_col: str):
        """Check class imbalance in target."""
        print("=" * 80)
        print("TARGET DISTRIBUTION & CLASS IMBALANCE")
        print("=" * 80)
        
        if target_col not in self.df.columns:
            print(f"⚠ Target column '{target_col}' not found")
            return
        
        value_counts = self.df[target_col].value_counts()
        percentages = (self.df[target_col].value_counts(normalize=True) * 100).round(2)
        
        print(f"\nTarget Column: {target_col}")
        print(f"Total Samples: {len(self.df)}")
        print(f"\nClass Distribution:")
        for label, count in value_counts.items():
            pct = percentages[label]
            print(f"  {label}: {count} samples ({pct}%)")
        
        # Calculate imbalance ratio
        if len(value_counts) == 2:
            ratio = value_counts.iloc[0] / value_counts.iloc[1]
            print(f"\nImbalance Ratio: {ratio:.2f}:1")
            if ratio > 3:
                print("⚠ Warning: Severe class imbalance detected (>3:1)")
            elif ratio > 1.5:
                print("⚠ Warning: Moderate class imbalance detected (>1.5:1)")
            else:
                print("✓ Balanced classes")
        
        print()
    
    def check_outliers(self, numeric_cols: list):
        """Check for extreme outliers."""
        print("=" * 80)
        print("OUTLIER DETECTION (NUMERIC FEATURES)")
        print("=" * 80)
        
        print(f"\nBasic Statistics for {len(numeric_cols)} Numeric Features:")
        print(self.df[numeric_cols].describe().round(2))
        print()
    
    def generate_report(self, target_col: str) -> Dict:
        """Generate comprehensive diagnostic report."""
        print("=" * 80)
        print("DIAGNOSTIC REPORT SUMMARY")
        print("=" * 80)
        
        report = {
            'total_samples': len(self.df),
            'total_features': len(self.df.columns),
            'missing_values': self.df.isnull().sum().sum(),
            'duplicate_rows': self.df.duplicated().sum(),
            'target_column': target_col,
        }
        
        if target_col in self.df.columns:
            value_counts = self.df[target_col].value_counts()
            report['class_distribution'] = value_counts.to_dict()
            report['class_percentages'] = (value_counts / len(self.df) * 100).round(2).to_dict()
        
        print(f"\n✓ Total Samples: {report['total_samples']}")
        print(f"✓ Total Features: {report['total_features']}")
        print(f"✓ Missing Values: {report['missing_values']}")
        print(f"✓ Duplicate Rows: {report['duplicate_rows']}")
        
        if target_col in self.df.columns:
            for label, count in report['class_distribution'].items():
                pct = report['class_percentages'][label]
                print(f"✓ Class {label}: {count} ({pct}%)")
        
        print("\n" + "=" * 80)
        print("✓ DATA INGESTION COMPLETE")
        print("=" * 80 + "\n")
        
        return report
    
    def remove_unnecessary_columns(self) -> pd.DataFrame:
        """Remove columns that are not essential for sepsis prediction."""
        print("=" * 80)
        print("REMOVING UNNECESSARY COLUMNS")
        print("=" * 80)
        
        # Columns to remove
        unnecessary_cols = [
            'Patient_ID', 'Unnamed: 0', 'Unit1', 'Unit2', 'Gender',
            'HospAdmTime', 'ICULOS', 'TroponinI', 'AST', 'Magnesium',
            'Phosphate', 'Calcium', 'AlkalinePhosphatase', 'Bilirubin_direct'
        ]
        
        # Find which columns exist in the dataframe
        cols_to_drop = [col for col in unnecessary_cols if col in self.df.columns]
        
        if cols_to_drop:
            print(f"\nRemoving {len(cols_to_drop)} unnecessary columns:")
            for col in cols_to_drop:
                print(f"  - {col}")
            
            self.df = self.df.drop(columns=cols_to_drop)
            print(f"\n✓ Columns removed. Remaining features: {len(self.df.columns)}")
        else:
            print("\n✓ No unnecessary columns found to remove")
        
        print()
        return self.df
    
    def run_validation(self) -> Tuple[pd.DataFrame, Dict]:
        """Run full validation pipeline."""
        # Load data
        self.load_data()
        
        # Remove unnecessary columns
        self.remove_unnecessary_columns()
        
        # Print basic info
        self.print_basic_info()
        
        # Identify columns
        col_info = self.identify_columns()
        target_col = col_info['target']
        
        # Check missing values
        self.check_missing_values()
        
        # Check duplicates
        self.check_duplicates()
        
        # Check target distribution
        if target_col:
            self.check_target_distribution(target_col)
        
        # Check outliers
        self.check_outliers(col_info['numeric'])
        
        # Generate report
        report = self.generate_report(target_col)
        
        return self.df, report


# Main execution
if __name__ == "__main__":
    import os
    
    # Try multiple paths
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
        print("⚠ Dataset.csv not found. Creating sample dataset...")
        # Create sample sepsis dataset
        np.random.seed(42)
        n_samples = 1000
        
        sample_data = {
            'patient_id': [f'p{i:06d}' for i in range(n_samples)],
            'age': np.random.randint(18, 90, n_samples),
            'gender': np.random.choice(['M', 'F'], n_samples),
            'HR': np.random.randint(60, 120, n_samples),
            'SBP': np.random.randint(100, 180, n_samples),
            'DBP': np.random.randint(60, 110, n_samples),
            'RR': np.random.randint(12, 30, n_samples),
            'SpO2': np.random.randint(90, 100, n_samples),
            'Temp': np.random.uniform(36.0, 39.5, n_samples),
            'WBC': np.random.uniform(4, 15, n_samples),
            'Lactate': np.random.uniform(0.5, 4, n_samples),
            'Glucose': np.random.randint(70, 200, n_samples),
            'sepsis': np.random.choice([0, 1], n_samples, p=[0.8, 0.2])
        }
        
        df_sample = pd.DataFrame(sample_data)
        df_sample.to_csv('Dataset.csv', index=False)
        print("✓ Sample dataset created: Dataset.csv\n")
        dataset_path = 'Dataset.csv'
    
    # Initialize module
    ingestion = DataIngestionModule(dataset_path)
    
    # Run validation
    df, report = ingestion.run_validation()
    
    print("✓ Data ready for feature engineering!")
