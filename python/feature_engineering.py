"""
Feature Engineering for HR Recruitment Funnel ML Model
Creates features for predicting candidate drop-off at each stage
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib

class FeatureEngineer:
    """Feature engineering for recruitment funnel prediction"""
    
    def __init__(self):
        self.label_encoders = {}
        self.scaler = StandardScaler()
        
    def create_features(self, df):
        """
        Create features for ML model
        
        Args:
            df: DataFrame with recruitment funnel data
            
        Returns:
            DataFrame with engineered features
        """
        print("🔧 Engineering features...")
        
        # Create a copy
        df_features = df.copy()
        
        # 1. CATEGORICAL ENCODING
        categorical_cols = ['Source', 'Job_Role', 'Department', 'Gender', 'EducationField']
        
        for col in categorical_cols:
            if col in df_features.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    df_features[f'{col}_encoded'] = self.label_encoders[col].fit_transform(df_features[col].astype(str))
                else:
                    df_features[f'{col}_encoded'] = self.label_encoders[col].transform(df_features[col].astype(str))
        
        # 2. NUMERICAL FEATURES
        if 'Age' in df_features.columns:
            df_features['Age_squared'] = df_features['Age'] ** 2
            df_features['Age_normalized'] = (df_features['Age'] - df_features['Age'].mean()) / df_features['Age'].std()
        
        if 'Education' in df_features.columns:
            df_features['Education_level'] = df_features['Education']
        
        # 3. STAGE-BASED FEATURES
        if 'Stage_Sequence' in df_features.columns:
            df_features['Stage_progress'] = df_features['Stage_Sequence'] / 8  # Normalize to 0-1
            df_features['Is_early_stage'] = (df_features['Stage_Sequence'] <= 3).astype(int)
            df_features['Is_late_stage'] = (df_features['Stage_Sequence'] >= 6).astype(int)
        
        # 4. TIME-BASED FEATURES
        if 'Days_Since_Application' in df_features.columns:
            df_features['Days_log'] = np.log1p(df_features['Days_Since_Application'])
            df_features['Is_slow_process'] = (df_features['Days_Since_Application'] > 50).astype(int)
        
        # 5. SOURCE EFFECTIVENESS FEATURES
        # Calculate historical success rate by source
        if 'Source' in df_features.columns and 'Status' in df_features.columns:
            source_success = df_features.groupby('Source')['Status'].apply(
                lambda x: (x == 'Hired').sum() / len(x) if len(x) > 0 else 0
            ).to_dict()
            df_features['Source_success_rate'] = df_features['Source'].map(source_success)
        
        # 6. INTERACTION FEATURES
        if 'Age' in df_features.columns and 'Education' in df_features.columns:
            df_features['Age_Education_interaction'] = df_features['Age'] * df_features['Education']
        
        print(f"✅ Created {len(df_features.columns)} features")
        
        return df_features
    
    def prepare_for_modeling(self, df, target_col='will_drop_off', feature_cols=None):
        """
        Prepare data for ML modeling
        
        Args:
            df: DataFrame with features
            target_col: Name of target column
            feature_cols: List of feature columns to use (None = auto-select)
            
        Returns:
            X (features), y (target)
        """
        print("\n📊 Preparing data for modeling...")
        
        # Auto-select feature columns if not provided
        if feature_cols is None:
            # Select all numeric columns except target and IDs
            exclude_cols = [target_col, 'Applicant_ID', 'Application_Date', 'Stage_Date', 
                          'Stage', 'Status', 'Source', 'Job_Role', 'Department', 
                          'Gender', 'EducationField']
            feature_cols = [col for col in df.columns 
                          if col not in exclude_cols and df[col].dtype in ['int64', 'float64']]
        
        print(f"   Using {len(feature_cols)} features:")
        for col in feature_cols:
            print(f"      - {col}")
        
        # Extract features and target
        X = df[feature_cols].copy()
        
        # Handle missing values
        X = X.fillna(X.median())
        
        # Extract target if it exists
        if target_col in df.columns:
            y = df[target_col]
        else:
            y = None
        
        print(f"✅ Data prepared: X shape = {X.shape}")
        if y is not None:
            print(f"   Target distribution: {y.value_counts().to_dict()}")
        
        return X, y, feature_cols
    
    def save(self, filepath='models/feature_engineer.pkl'):
        """Save feature engineer (encoders and scaler)"""
        joblib.dump({
            'label_encoders': self.label_encoders,
            'scaler': self.scaler
        }, filepath)
        print(f"✅ Feature engineer saved to {filepath}")
    
    @classmethod
    def load(cls, filepath='models/feature_engineer.pkl'):
        """Load saved feature engineer"""
        data = joblib.load(filepath)
        fe = cls()
        fe.label_encoders = data['label_encoders']
        fe.scaler = data['scaler']
        print(f"✅ Feature engineer loaded from {filepath}")
        return fe


def create_target_variable(df):
    """
    Create target variable: will the candidate drop off at next stage?
    
    Args:
        df: DataFrame with recruitment funnel data
        
    Returns:
        DataFrame with 'will_drop_off' column added
    """
    print("\n🎯 Creating target variable...")
    
    df_target = df.copy()
    
    # For each applicant, check if they were rejected at current stage
    df_target['will_drop_off'] = (df_target['Status'] == 'Rejected').astype(int)
    
    # Count drop-offs
    drop_off_count = df_target['will_drop_off'].sum()
    total_count = len(df_target)
    drop_off_rate = (drop_off_count / total_count * 100)
    
    print(f"   Total records: {total_count:,}")
    print(f"   Drop-offs: {drop_off_count:,} ({drop_off_rate:.1f}%)")
    print(f"   Continued: {total_count - drop_off_count:,} ({100 - drop_off_rate:.1f}%)")
    
    return df_target


if __name__ == "__main__":
    # Test feature engineering
    print("=" * 70)
    print("FEATURE ENGINEERING TEST")
    print("=" * 70)
    
    # Load data
    df = pd.read_csv('data/hr_recruitment_funnel.csv')
    print(f"\n📂 Loaded {len(df):,} records")
    
    # Create target variable
    df = create_target_variable(df)
    
    # Initialize feature engineer
    fe = FeatureEngineer()
    
    # Create features
    df_features = fe.create_features(df)
    
    # Prepare for modeling
    X, y, feature_cols = fe.prepare_for_modeling(df_features, target_col='will_drop_off')
    
    print(f"\n📊 Final dataset:")
    print(f"   Features shape: {X.shape}")
    print(f"   Target shape: {y.shape}")
    print(f"   Feature names: {feature_cols}")
    
    # Save feature engineer
    fe.save()
    
    print("\n" + "=" * 70)
    print("✅ FEATURE ENGINEERING COMPLETE")
    print("=" * 70)
