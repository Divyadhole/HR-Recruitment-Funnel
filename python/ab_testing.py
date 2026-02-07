"""
A/B Testing Framework for Recruitment Process Optimization
Simulates and analyzes process improvement experiments
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

class ABTestingFramework:
    """Framework for A/B testing recruitment process changes"""
    
    def __init__(self, df):
        """
        Initialize A/B testing framework
        
        Args:
            df: DataFrame with recruitment funnel data
        """
        self.df = df
        self.results = {}
    
    def simulate_intervention(self, stage, improvement_rate, sample_size=None):
        """
        Simulate the effect of an intervention at a specific stage
        
        Args:
            stage: Stage name to apply intervention
            improvement_rate: Expected improvement (e.g., 0.10 for 10% improvement)
            sample_size: Number of applicants to simulate (None = use all)
            
        Returns:
            Dictionary with simulation results
        """
        print(f"\n🧪 Simulating intervention at {stage}")
        print(f"   Expected improvement: {improvement_rate*100:.1f}%")
        
        # Get baseline data
        stage_data = self.df[self.df['Stage'] == stage].copy()
        
        if sample_size:
            stage_data = stage_data.sample(n=min(sample_size, len(stage_data)), random_state=42)
        
        # Calculate baseline metrics
        baseline_pass_rate = (stage_data['Status'] != 'Rejected').mean()
        baseline_passed = (stage_data['Status'] != 'Rejected').sum()
        
        # Simulate intervention (increase pass rate)
        new_pass_rate = min(baseline_pass_rate * (1 + improvement_rate), 1.0)
        expected_passed = int(len(stage_data) * new_pass_rate)
        additional_passed = expected_passed - baseline_passed
        
        results = {
            'stage': stage,
            'sample_size': len(stage_data),
            'baseline_pass_rate': baseline_pass_rate,
            'new_pass_rate': new_pass_rate,
            'baseline_passed': baseline_passed,
            'expected_passed': expected_passed,
            'additional_passed': additional_passed,
            'improvement_pct': ((new_pass_rate - baseline_pass_rate) / baseline_pass_rate * 100)
        }
        
        print(f"\n   Baseline pass rate: {baseline_pass_rate*100:.1f}%")
        print(f"   New pass rate: {new_pass_rate*100:.1f}%")
        print(f"   Additional candidates passing: +{additional_passed}")
        
        return results
    
    def calculate_statistical_significance(self, control_success, control_total, 
                                          treatment_success, treatment_total, alpha=0.05):
        """
        Calculate statistical significance using chi-square test
        
        Args:
            control_success: Number of successes in control group
            control_total: Total in control group
            treatment_success: Number of successes in treatment group
            treatment_total: Total in treatment group
            alpha: Significance level (default 0.05)
            
        Returns:
            Dictionary with test results
        """
        # Create contingency table
        contingency_table = np.array([
            [control_success, control_total - control_success],
            [treatment_success, treatment_total - treatment_success]
        ])
        
        # Chi-square test
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
        
        # Calculate effect size (Cohen's h)
        p1 = control_success / control_total
        p2 = treatment_success / treatment_total
        cohens_h = 2 * (np.arcsin(np.sqrt(p2)) - np.arcsin(np.sqrt(p1)))
        
        results = {
            'chi_square': chi2,
            'p_value': p_value,
            'is_significant': p_value < alpha,
            'alpha': alpha,
            'cohens_h': cohens_h,
            'control_rate': p1,
            'treatment_rate': p2,
            'relative_improvement': ((p2 - p1) / p1 * 100) if p1 > 0 else 0
        }
        
        return results
    
    def power_analysis(self, baseline_rate, expected_improvement, alpha=0.05, power=0.80):
        """
        Calculate required sample size for desired statistical power
        
        Args:
            baseline_rate: Current conversion rate
            expected_improvement: Expected improvement (e.g., 0.10 for 10%)
            alpha: Significance level
            power: Desired statistical power
            
        Returns:
            Required sample size per group
        """
        from statsmodels.stats.power import zt_ind_solve_power
        
        new_rate = baseline_rate * (1 + expected_improvement)
        effect_size = 2 * (np.arcsin(np.sqrt(new_rate)) - np.arcsin(np.sqrt(baseline_rate)))
        
        sample_size = zt_ind_solve_power(
            effect_size=effect_size,
            alpha=alpha,
            power=power,
            alternative='two-sided'
        )
        
        return int(np.ceil(sample_size))
    
    def recommend_test_duration(self, daily_applicants, required_sample_size):
        """
        Recommend test duration based on traffic
        
        Args:
            daily_applicants: Average daily applicants
            required_sample_size: Required sample size per group
            
        Returns:
            Recommended duration in days
        """
        total_needed = required_sample_size * 2  # Control + Treatment
        days_needed = np.ceil(total_needed / daily_applicants)
        
        return int(days_needed)
    
    def visualize_ab_test(self, control_rate, treatment_rate, control_n, treatment_n):
        """Create visualization of A/B test results"""
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Conversion rates comparison
        rates = [control_rate * 100, treatment_rate * 100]
        labels = ['Control', 'Treatment']
        colors = ['#94a3b8', '#10b981']
        
        axes[0].bar(labels, rates, color=colors, edgecolor='black', linewidth=1.5)
        axes[0].set_ylabel('Conversion Rate (%)', fontsize=12, fontweight='bold')
        axes[0].set_title('A/B Test: Conversion Rate Comparison', fontsize=14, fontweight='bold')
        axes[0].set_ylim(0, max(rates) * 1.2)
        
        for i, (label, rate) in enumerate(zip(labels, rates)):
            axes[0].text(i, rate + max(rates)*0.02, f'{rate:.1f}%', 
                        ha='center', fontsize=11, fontweight='bold')
        
        # Confidence intervals
        control_ci = 1.96 * np.sqrt(control_rate * (1 - control_rate) / control_n)
        treatment_ci = 1.96 * np.sqrt(treatment_rate * (1 - treatment_rate) / treatment_n)
        
        ci_data = pd.DataFrame({
            'Group': labels,
            'Rate': rates,
            'CI_Lower': [(control_rate - control_ci) * 100, (treatment_rate - treatment_ci) * 100],
            'CI_Upper': [(control_rate + control_ci) * 100, (treatment_rate + treatment_ci) * 100]
        })
        
        axes[1].errorbar(
            ci_data['Group'], ci_data['Rate'],
            yerr=[ci_data['Rate'] - ci_data['CI_Lower'], ci_data['CI_Upper'] - ci_data['Rate']],
            fmt='o', markersize=10, capsize=5, capthick=2, color='#3b82f6', linewidth=2
        )
        axes[1].set_ylabel('Conversion Rate (%)', fontsize=12, fontweight='bold')
        axes[1].set_title('95% Confidence Intervals', fontsize=14, fontweight='bold')
        axes[1].grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('visualizations/ab_test_results.png', dpi=300, bbox_inches='tight')
        print("\n✅ Saved: visualizations/ab_test_results.png")
        plt.close()


def main():
    """Run A/B testing examples"""
    print("=" * 70)
    print("A/B TESTING FRAMEWORK - RECRUITMENT OPTIMIZATION")
    print("=" * 70)
    
    # Load data
    df = pd.read_csv('data/hr_recruitment_funnel.csv')
    print(f"\n📂 Loaded {len(df):,} records")
    
    # Initialize framework
    ab_test = ABTestingFramework(df)
    
    # Example 1: Test technical round prep resources
    print("\n" + "=" * 70)
    print("TEST 1: Technical Round Prep Resources")
    print("=" * 70)
    
    tech_results = ab_test.simulate_intervention(
        stage='Technical Round',
        improvement_rate=0.15,  # 15% improvement
        sample_size=500
    )
    
    # Calculate statistical significance
    sig_results = ab_test.calculate_statistical_significance(
        control_success=int(tech_results['baseline_passed']),
        control_total=tech_results['sample_size'],
        treatment_success=tech_results['expected_passed'],
        treatment_total=tech_results['sample_size']
    )
    
    print(f"\n📊 Statistical Significance:")
    print(f"   P-value: {sig_results['p_value']:.4f}")
    print(f"   Significant: {'✅ YES' if sig_results['is_significant'] else '❌ NO'}")
    print(f"   Effect size (Cohen's h): {sig_results['cohens_h']:.3f}")
    
    # Power analysis
    required_n = ab_test.power_analysis(
        baseline_rate=tech_results['baseline_pass_rate'],
        expected_improvement=0.15,
        power=0.80
    )
    
    print(f"\n📈 Power Analysis:")
    print(f"   Required sample size per group: {required_n:,}")
    print(f"   Total participants needed: {required_n * 2:,}")
    
    # Visualize
    ab_test.visualize_ab_test(
        control_rate=sig_results['control_rate'],
        treatment_rate=sig_results['treatment_rate'],
        control_n=tech_results['sample_size'],
        treatment_n=tech_results['sample_size']
    )
    
    # Example 2: Test source optimization
    print("\n" + "=" * 70)
    print("TEST 2: Budget Reallocation to High-Performing Sources")
    print("=" * 70)
    
    # Calculate current vs optimized scenario
    source_stats = df.groupby('Source').agg({
        'Applicant_ID': 'nunique',
        'Status': lambda x: (x == 'Hired').sum()
    }).reset_index()
    source_stats.columns = ['Source', 'Applicants', 'Hired']
    source_stats['Hire_Rate'] = source_stats['Hired'] / source_stats['Applicants']
    
    print("\n📊 Current Source Performance:")
    print(source_stats.to_string(index=False))
    
    # Recommendation
    best_source = source_stats.loc[source_stats['Hire_Rate'].idxmax()]
    worst_source = source_stats.loc[source_stats['Hire_Rate'].idxmin()]
    
    print(f"\n💡 Recommendation:")
    print(f"   Shift budget from {worst_source['Source']} ({worst_source['Hire_Rate']*100:.1f}% hire rate)")
    print(f"   to {best_source['Source']} ({best_source['Hire_Rate']*100:.1f}% hire rate)")
    print(f"   Expected improvement: +{((best_source['Hire_Rate'] - worst_source['Hire_Rate']) / worst_source['Hire_Rate'] * 100):.1f}%")
    
    print("\n" + "=" * 70)
    print("✅ A/B TESTING ANALYSIS COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()
