"""
Machine Learning Model for Predicting Candidate Drop-off
Trains Random Forest and Gradient Boosting models to predict recruitment funnel drop-off
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (classification_report, confusion_matrix, roc_auc_score,
                            roc_curve, precision_recall_curve, f1_score)
from imblearn.over_sampling import SMOTE
import joblib
import warnings
warnings.filterwarnings('ignore')

from feature_engineering import FeatureEngineer, create_target_variable

class RecruitmentMLModel:
    """ML Model for predicting candidate drop-off"""
    
    def __init__(self, model_type='random_forest'):
        """
        Initialize ML model
        
        Args:
            model_type: 'random_forest' or 'gradient_boosting'
        """
        self.model_type = model_type
        self.model = None
        self.feature_cols = None
        self.feature_importance = None
        
    def train(self, X_train, y_train, use_smote=True, tune_hyperparameters=False):
        """
        Train the model
        
        Args:
            X_train: Training features
            y_train: Training target
            use_smote: Whether to use SMOTE for class imbalance
            tune_hyperparameters: Whether to perform grid search
        """
        print(f"\n🤖 Training {self.model_type.upper()} model...")
        
        # Handle class imbalance with SMOTE
        if use_smote:
            print("   Applying SMOTE for class balance...")
            smote = SMOTE(random_state=42)
            X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)
            print(f"   Before SMOTE: {y_train.value_counts().to_dict()}")
            print(f"   After SMOTE: {y_train_balanced.value_counts().to_dict()}")
        else:
            X_train_balanced, y_train_balanced = X_train, y_train
        
        # Initialize model
        if self.model_type == 'random_forest':
            if tune_hyperparameters:
                print("   Tuning hyperparameters...")
                param_grid = {
                    'n_estimators': [100, 200],
                    'max_depth': [10, 20, None],
                    'min_samples_split': [2, 5],
                    'min_samples_leaf': [1, 2]
                }
                base_model = RandomForestClassifier(random_state=42, n_jobs=-1)
                self.model = GridSearchCV(base_model, param_grid, cv=3, scoring='roc_auc', n_jobs=-1)
            else:
                self.model = RandomForestClassifier(
                    n_estimators=200,
                    max_depth=20,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    random_state=42,
                    n_jobs=-1,
                    class_weight='balanced'
                )
        
        elif self.model_type == 'gradient_boosting':
            if tune_hyperparameters:
                print("   Tuning hyperparameters...")
                param_grid = {
                    'max_depth': [3, 5, 7],
                    'learning_rate': [0.01, 0.1],
                    'n_estimators': [100, 200],
                    'subsample': [0.8, 1.0]
                }
                base_model = GradientBoostingClassifier(random_state=42)
                self.model = GridSearchCV(base_model, param_grid, cv=3, scoring='roc_auc', n_jobs=-1)
            else:
                self.model = GradientBoostingClassifier(
                    max_depth=5,
                    learning_rate=0.1,
                    n_estimators=200,
                    subsample=0.8,
                    random_state=42
                )
        
        # Train model
        self.model.fit(X_train_balanced, y_train_balanced)
        
        # Extract best model if grid search was used
        if tune_hyperparameters:
            print(f"   Best parameters: {self.model.best_params_}")
            self.model = self.model.best_estimator_
        
        # Calculate feature importance
        if hasattr(self.model, 'feature_importances_'):
            self.feature_importance = pd.DataFrame({
                'feature': X_train.columns,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
        
        print("✅ Model training complete!")
        
    def evaluate(self, X_test, y_test, save_plots=True):
        """
        Evaluate model performance
        
        Args:
            X_test: Test features
            y_test: Test target
            save_plots: Whether to save evaluation plots
            
        Returns:
            Dictionary of evaluation metrics
        """
        print("\n📊 Evaluating model performance...")
        
        # Predictions
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        metrics = {
            'accuracy': (y_pred == y_test).mean(),
            'roc_auc': roc_auc_score(y_test, y_pred_proba),
            'f1_score': f1_score(y_test, y_pred)
        }
        
        print(f"\n   Accuracy: {metrics['accuracy']:.3f}")
        print(f"   ROC-AUC: {metrics['roc_auc']:.3f}")
        print(f"   F1 Score: {metrics['f1_score']:.3f}")
        
        # Classification report
        print("\n   Classification Report:")
        print(classification_report(y_test, y_pred, target_names=['Continue', 'Drop-off']))
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        print("\n   Confusion Matrix:")
        print(f"   True Negatives: {cm[0,0]}, False Positives: {cm[0,1]}")
        print(f"   False Negatives: {cm[1,0]}, True Positives: {cm[1,1]}")
        
        if save_plots:
            self._save_evaluation_plots(y_test, y_pred, y_pred_proba, cm, metrics)
        
        return metrics
    
    def _save_evaluation_plots(self, y_test, y_pred, y_pred_proba, cm, metrics):
        """Save evaluation visualizations"""
        print("\n📈 Creating evaluation plots...")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Confusion Matrix
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[0,0])
        axes[0,0].set_title('Confusion Matrix', fontsize=14, fontweight='bold')
        axes[0,0].set_ylabel('True Label')
        axes[0,0].set_xlabel('Predicted Label')
        axes[0,0].set_xticklabels(['Continue', 'Drop-off'])
        axes[0,0].set_yticklabels(['Continue', 'Drop-off'])
        
        # 2. ROC Curve
        fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
        axes[0,1].plot(fpr, tpr, linewidth=2, label=f"ROC (AUC = {metrics['roc_auc']:.3f})")
        axes[0,1].plot([0, 1], [0, 1], 'k--', linewidth=1, label='Random')
        axes[0,1].set_xlabel('False Positive Rate', fontsize=12)
        axes[0,1].set_ylabel('True Positive Rate', fontsize=12)
        axes[0,1].set_title('ROC Curve', fontsize=14, fontweight='bold')
        axes[0,1].legend()
        axes[0,1].grid(alpha=0.3)
        
        # 3. Precision-Recall Curve
        precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
        axes[1,0].plot(recall, precision, linewidth=2, color='green')
        axes[1,0].set_xlabel('Recall', fontsize=12)
        axes[1,0].set_ylabel('Precision', fontsize=12)
        axes[1,0].set_title('Precision-Recall Curve', fontsize=14, fontweight='bold')
        axes[1,0].grid(alpha=0.3)
        
        # 4. Feature Importance (Top 15)
        if self.feature_importance is not None:
            top_features = self.feature_importance.head(15)
            axes[1,1].barh(range(len(top_features)), top_features['importance'], color='steelblue')
            axes[1,1].set_yticks(range(len(top_features)))
            axes[1,1].set_yticklabels(top_features['feature'])
            axes[1,1].set_xlabel('Importance', fontsize=12)
            axes[1,1].set_title('Top 15 Feature Importance', fontsize=14, fontweight='bold')
            axes[1,1].invert_yaxis()
        
        plt.tight_layout()
        plt.savefig('visualizations/ml_model_evaluation.png', dpi=300, bbox_inches='tight')
        print("✅ Saved: visualizations/ml_model_evaluation.png")
        plt.close()
        
        # Separate feature importance plot
        if self.feature_importance is not None:
            plt.figure(figsize=(12, 8))
            top_20 = self.feature_importance.head(20)
            plt.barh(range(len(top_20)), top_20['importance'], color='darkgreen', edgecolor='black')
            plt.yticks(range(len(top_20)), top_20['feature'])
            plt.xlabel('Importance Score', fontsize=12, fontweight='bold')
            plt.ylabel('Feature', fontsize=12, fontweight='bold')
            plt.title('Top 20 Most Important Features for Drop-off Prediction', 
                     fontsize=14, fontweight='bold', pad=20)
            plt.gca().invert_yaxis()
            plt.grid(axis='x', alpha=0.3)
            plt.tight_layout()
            plt.savefig('visualizations/feature_importance.png', dpi=300, bbox_inches='tight')
            print("✅ Saved: visualizations/feature_importance.png")
            plt.close()
    
    def predict_drop_off_probability(self, X):
        """
        Predict drop-off probability for new candidates
        
        Args:
            X: Features for prediction
            
        Returns:
            Array of drop-off probabilities
        """
        return self.model.predict_proba(X)[:, 1]
    
    def save(self, filepath='models/recruitment_model.pkl'):
        """Save trained model"""
        model_data = {
            'model': self.model,
            'model_type': self.model_type,
            'feature_importance': self.feature_importance
        }
        joblib.dump(model_data, filepath)
        print(f"✅ Model saved to {filepath}")
    
    @classmethod
    def load(cls, filepath='models/recruitment_model.pkl'):
        """Load saved model"""
        model_data = joblib.load(filepath)
        ml_model = cls(model_type=model_data['model_type'])
        ml_model.model = model_data['model']
        ml_model.feature_importance = model_data['feature_importance']
        print(f"✅ Model loaded from {filepath}")
        return ml_model


def main():
    """Main training pipeline"""
    print("=" * 70)
    print("ML MODEL TRAINING PIPELINE")
    print("=" * 70)
    
    # 1. Load data
    print("\n📂 Loading data...")
    df = pd.read_csv('data/hr_recruitment_funnel.csv')
    print(f"✅ Loaded {len(df):,} records")
    
    # 2. Create target variable
    df = create_target_variable(df)
    
    # 3. Feature engineering
    fe = FeatureEngineer()
    df_features = fe.create_features(df)
    X, y, feature_cols = fe.prepare_for_modeling(df_features, target_col='will_drop_off')
    
    # 4. Train-test split
    print("\n✂️  Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"   Training set: {len(X_train):,} samples")
    print(f"   Test set: {len(X_test):,} samples")
    
    # 5. Train Random Forest
    print("\n" + "=" * 70)
    print("TRAINING RANDOM FOREST MODEL")
    print("=" * 70)
    rf_model = RecruitmentMLModel(model_type='random_forest')
    rf_model.train(X_train, y_train, use_smote=True)
    rf_metrics = rf_model.evaluate(X_test, y_test)
    rf_model.save('models/random_forest_model.pkl')
    
    # 6. Train Gradient Boosting
    print("\n" + "=" * 70)
    print("TRAINING GRADIENT BOOSTING MODEL")
    print("=" * 70)
    gb_model = RecruitmentMLModel(model_type='gradient_boosting')
    gb_model.train(X_train, y_train, use_smote=True)
    gb_metrics = gb_model.evaluate(X_test, y_test, save_plots=False)
    gb_model.save('models/gradient_boosting_model.pkl')
    
    # 7. Compare models
    print("\n" + "=" * 70)
    print("MODEL COMPARISON")
    print("=" * 70)
    comparison = pd.DataFrame({
        'Model': ['Random Forest', 'Gradient Boosting'],
        'Accuracy': [rf_metrics['accuracy'], gb_metrics['accuracy']],
        'ROC-AUC': [rf_metrics['roc_auc'], gb_metrics['roc_auc']],
        'F1 Score': [rf_metrics['f1_score'], gb_metrics['f1_score']]
    })
    print(comparison.to_string(index=False))
    
    # Determine best model
    best_model_name = 'Random Forest' if rf_metrics['roc_auc'] > gb_metrics['roc_auc'] else 'Gradient Boosting'
    best_model = rf_model if best_model_name == 'Random Forest' else gb_model
    
    print(f"\n🏆 Best Model: {best_model_name} (ROC-AUC: {max(rf_metrics['roc_auc'], gb_metrics['roc_auc']):.3f})")
    
    # Save best model as default
    best_model.save('models/best_model.pkl')
    
    # Save feature engineer
    fe.save('models/feature_engineer.pkl')
    
    # Print top features
    print("\n🔝 Top 10 Most Important Features:")
    if best_model.feature_importance is not None:
        for idx, row in best_model.feature_importance.head(10).iterrows():
            print(f"   {idx+1}. {row['feature']:.<40} {row['importance']:.4f}")
    
    print("\n" + "=" * 70)
    print("✅ ML MODEL TRAINING COMPLETE!")
    print("=" * 70)
    print("\nSaved files:")
    print("   - models/random_forest_model.pkl")
    print("   - models/gradient_boosting_model.pkl")
    print("   - models/best_model.pkl")
    print("   - models/feature_engineer.pkl")
    print("   - visualizations/ml_model_evaluation.png")
    print("   - visualizations/feature_importance.png")
    print("=" * 70)


if __name__ == "__main__":
    main()
