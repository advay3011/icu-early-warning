"""
Dataset Enrichment - Add realistic features
Adds demographics, comorbidities, clinical context, and medications
"""

import pandas as pd
import numpy as np
import os

def add_demographics(df):
    """Add age, gender, BMI to dataset"""
    print("Adding demographics...")
    
    # Age: realistic ICU distribution (mean 65, older skewed)
    df['age'] = np.random.normal(loc=65, scale=15, size=len(df))
    df['age'] = df['age'].clip(18, 95)  # Realistic range
    
    # Gender: 50/50 split
    df['gender'] = np.random.choice(['Male', 'Female'], size=len(df), p=[0.5, 0.5])
    
    # BMI: realistic distribution
    df['bmi'] = np.random.normal(loc=28, scale=6, size=len(df))
    df['bmi'] = df['bmi'].clip(15, 50)  # Realistic range
    
    print(f"  ✓ Age: mean={df['age'].mean():.1f}, range=[{df['age'].min():.0f}, {df['age'].max():.0f}]")
    print(f"  ✓ Gender: {(df['gender']=='Male').sum()} Male, {(df['gender']=='Female').sum()} Female")
    print(f"  ✓ BMI: mean={df['bmi'].mean():.1f}, range=[{df['bmi'].min():.1f}, {df['bmi'].max():.1f}]")
    
    return df

def add_comorbidities(df):
    """Add comorbidity flags (realistic prevalence)"""
    print("\nAdding comorbidities...")
    
    comorbidities = {
        'diabetes': 0.30,           # 30% prevalence
        'hypertension': 0.40,       # 40% prevalence
        'heart_disease': 0.25,      # 25% prevalence
        'kidney_disease': 0.15,     # 15% prevalence
        'liver_disease': 0.10,      # 10% prevalence
        'immunosuppressed': 0.20,   # 20% prevalence
        'copd': 0.12,               # 12% prevalence
        'cancer': 0.08,             # 8% prevalence
    }
    
    for condition, prevalence in comorbidities.items():
        df[condition] = np.random.binomial(1, prevalence, size=len(df))
        count = df[condition].sum()
        pct = (count / len(df)) * 100
        print(f"  ✓ {condition}: {count} patients ({pct:.1f}%)")
    
    # Comorbidity score (0-8)
    df['comorbidity_score'] = df[[col for col in comorbidities.keys()]].sum(axis=1)
    print(f"  ✓ Comorbidity score: mean={df['comorbidity_score'].mean():.2f}")
    
    return df

def add_infection_source(df):
    """Add infection source information"""
    print("\nAdding infection source...")
    
    sources = ['respiratory', 'urinary', 'abdominal', 'bloodstream', 'other']
    probabilities = [0.40, 0.30, 0.15, 0.10, 0.05]
    
    df['infection_source'] = np.random.choice(sources, size=len(df), p=probabilities)
    
    for source in sources:
        count = (df['infection_source'] == source).sum()
        pct = (count / len(df)) * 100
        print(f"  ✓ {source}: {count} ({pct:.1f}%)")
    
    return df

def add_admission_reason(df):
    """Add admission reason"""
    print("\nAdding admission reason...")
    
    reasons = ['trauma', 'surgery', 'infection', 'cardiac', 'respiratory', 'other']
    probabilities = [0.15, 0.25, 0.20, 0.15, 0.15, 0.10]
    
    df['admission_reason'] = np.random.choice(reasons, size=len(df), p=probabilities)
    
    for reason in reasons:
        count = (df['admission_reason'] == reason).sum()
        pct = (count / len(df)) * 100
        print(f"  ✓ {reason}: {count} ({pct:.1f}%)")
    
    return df

def add_medications(df):
    """Add medication flags"""
    print("\nAdding medications...")
    
    medications = {
        'on_antibiotics': 0.70,         # 70% on antibiotics
        'on_vasopressors': 0.30,        # 30% on vasopressors
        'on_sedatives': 0.60,           # 60% sedated
        'on_anticoagulation': 0.40,     # 40% anticoagulated
        'on_steroids': 0.25,            # 25% on steroids
        'on_insulin': 0.50,             # 50% on insulin
        'on_mechanical_ventilation': 0.35,  # 35% intubated
    }
    
    for med, prevalence in medications.items():
        df[med] = np.random.binomial(1, prevalence, size=len(df))
        count = df[med].sum()
        pct = (count / len(df)) * 100
        print(f"  ✓ {med}: {count} patients ({pct:.1f}%)")
    
    # Medication intensity score
    df['medication_intensity'] = df[[col for col in medications.keys()]].sum(axis=1)
    print(f"  ✓ Medication intensity: mean={df['medication_intensity'].mean():.2f}")
    
    return df

def add_clinical_severity(df):
    """Add clinical severity indicators"""
    print("\nAdding clinical severity indicators...")
    
    # SIRS criteria (0-4)
    df['sirs_score'] = 0
    if 'Temp' in df.columns:
        df['sirs_score'] += (df['Temp'] > 38).astype(int)
    if 'HR' in df.columns:
        df['sirs_score'] += (df['HR'] > 100).astype(int)
    if 'Resp' in df.columns:
        df['sirs_score'] += (df['Resp'] > 20).astype(int)
    if 'WBC' in df.columns:
        df['sirs_score'] += (df['WBC'] > 12).astype(int)
    
    print(f"  ✓ SIRS score: mean={df['sirs_score'].mean():.2f}")
    
    # qSOFA criteria (0-3)
    df['qsofa_score'] = 0
    if 'SBP' in df.columns:
        df['qsofa_score'] += (df['SBP'] < 100).astype(int)
    if 'Resp' in df.columns:
        df['qsofa_score'] += (df['Resp'] > 22).astype(int)
    # Altered mental status (simulated)
    df['qsofa_score'] += np.random.binomial(1, 0.15, size=len(df))
    
    print(f"  ✓ qSOFA score: mean={df['qsofa_score'].mean():.2f}")
    
    return df

def enrich_dataset(input_path, output_path=None):
    """Main enrichment function"""
    print("=" * 80)
    print("DATASET ENRICHMENT")
    print("=" * 80)
    
    # Load dataset
    print(f"\nLoading dataset from {input_path}...")
    df = pd.read_csv(input_path)
    print(f"✓ Loaded {len(df)} rows, {len(df.columns)} columns")
    
    # Add features
    df = add_demographics(df)
    df = add_comorbidities(df)
    df = add_infection_source(df)
    df = add_admission_reason(df)
    df = add_medications(df)
    df = add_clinical_severity(df)
    
    # Summary
    print("\n" + "=" * 80)
    print("ENRICHMENT COMPLETE")
    print("=" * 80)
    print(f"\nOriginal features: 44")
    print(f"New features added: {len(df.columns) - 44}")
    print(f"Total features: {len(df.columns)}")
    
    # Save
    if output_path is None:
        output_path = input_path.replace('.csv', '_enriched.csv')
    
    df.to_csv(output_path, index=False)
    print(f"\n✓ Enriched dataset saved to {output_path}")
    
    return df

if __name__ == "__main__":
    # Find dataset
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
        print("❌ Dataset.csv not found")
        print("Please ensure Dataset.csv is in the current directory")
    else:
        # Enrich dataset
        df = enrich_dataset(dataset_path)
        
        print("\n" + "=" * 80)
        print("SAMPLE OF ENRICHED DATA")
        print("=" * 80)
        print(df.head())
        
        print("\n" + "=" * 80)
        print("FEATURE SUMMARY")
        print("=" * 80)
        print(df.describe())
