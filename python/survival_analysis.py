"""
HR Recruitment Funnel - Python Visualization & Survival Analysis
Creates 5 key visualizations for the recruitment funnel project
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

print("=" * 70)
print("HR RECRUITMENT FUNNEL - VISUALIZATION & ANALYSIS")
print("=" * 70)

# Load data
print("\n📂 Loading recruitment funnel data...")
df = pd.read_csv('data/hr_recruitment_funnel.csv')
print(f"✅ Loaded {len(df):,} records")

# ======================================================================
# 1. RECRUITMENT FUNNEL VISUALIZATION
# ======================================================================
print("\n📊 Creating Visualization 1: Recruitment Funnel...")

funnel_data = df.groupby(['Stage', 'Stage_Sequence'])['Applicant_ID'].nunique().reset_index()
funnel_data = funnel_data.sort_values('Stage_Sequence')
funnel_data.columns = ['Stage', 'Sequence', 'Applicants']

plt.figure(figsize=(14, 8))
colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(funnel_data)))
bars = plt.barh(funnel_data['Stage'], funnel_data['Applicants'], color=colors, edgecolor='navy', linewidth=1.5)

plt.xlabel('Number of Applicants', fontsize=12, fontweight='bold')
plt.ylabel('Recruitment Stage', fontsize=12, fontweight='bold')
plt.title('HR Recruitment Funnel - Applicants by Stage', fontsize=16, fontweight='bold', pad=20)
plt.gca().invert_yaxis()

# Add values on bars
for idx, (bar, row) in enumerate(zip(bars, funnel_data.itertuples())):
    width = bar.get_width()
    plt.text(width + 20, bar.get_y() + bar.get_height()/2, 
             f'{row.Applicants:,}', 
             va='center', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('visualizations/recruitment_funnel.png', dpi=300, bbox_inches='tight')
print("✅ Saved: visualizations/recruitment_funnel.png")
plt.close()

# ======================================================================
# 2. DROP-OFF ANALYSIS
# ======================================================================
print("📊 Creating Visualization 2: Drop-off Analysis...")

drop_off = []
for i in range(len(funnel_data) - 1):
    current = funnel_data.iloc[i]['Applicants']
    next_stage = funnel_data.iloc[i + 1]['Applicants']
    drop_rate = ((current - next_stage) / current) * 100
    drop_off.append({
        'Stage': funnel_data.iloc[i]['Stage'],
        'Drop_Off_Rate': drop_rate
    })

drop_off_df = pd.DataFrame(drop_off)

plt.figure(figsize=(14, 8))
colors_drop = ['#d62728' if x > 40 else '#ff7f0e' if x > 25 else '#2ca02c' for x in drop_off_df['Drop_Off_Rate']]
bars = plt.bar(range(len(drop_off_df)), drop_off_df['Drop_Off_Rate'], color=colors_drop, edgecolor='black', linewidth=1.5)

plt.xticks(range(len(drop_off_df)), drop_off_df['Stage'], rotation=45, ha='right')
plt.ylabel('Drop-off Rate (%)', fontsize=12, fontweight='bold')
plt.xlabel('Recruitment Stage', fontsize=12, fontweight='bold')
plt.title('Drop-off Rate by Recruitment Stage', fontsize=16, fontweight='bold', pad=20)

# Add horizontal line at highest drop-off
max_drop = drop_off_df['Drop_Off_Rate'].max()
plt.axhline(y=max_drop, color='red', linestyle='--', linewidth=2, alpha=0.7, 
            label=f'Highest Drop-off: {max_drop:.1f}%')

# Add values on bars
for idx, (bar, rate) in enumerate(zip(bars, drop_off_df['Drop_Off_Rate'])):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height + 1, 
             f'{rate:.1f}%', 
             ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.legend(fontsize=11)
plt.tight_layout()
plt.savefig('visualizations/drop_off_analysis.png', dpi=300, bbox_inches='tight')
print("✅ Saved: visualizations/drop_off_analysis.png")
plt.close()

# Print drop-off statistics
print(f"\n📉 Drop-off Rates:")
for _, row in drop_off_df.sort_values('Drop_Off_Rate', ascending=False).iterrows():
    print(f"   {row['Stage']:.<35} {row['Drop_Off_Rate']:>5.1f}%")

# ======================================================================
# 3. SOURCE EFFECTIVENESS
# ======================================================================
print("\n📊 Creating Visualization 3: Source Effectiveness...")

source_perf = df.groupby('Source').agg({
    'Applicant_ID': 'nunique',
    'Days_Since_Application': 'mean'
}).round(2)

# Count hired
hired = df[df['Stage'] == 'Hired'].groupby('Source')['Applicant_ID'].nunique()
source_perf['Hired'] = hired.reindex(source_perf.index, fill_value=0)
source_perf['Hire_Rate'] = (source_perf['Hired'] / source_perf['Applicant_ID'] * 100).round(2)
source_perf = source_perf.sort_values('Hire_Rate', ascending=False)

print(f"\n🎯 Source Effectiveness:")
print(source_perf)

# Calculate ratios
if 'LinkedIn' in source_perf.index and 'Naukri' in source_perf.index:
    linkedin_rate = source_perf.loc['LinkedIn', 'Hire_Rate']
    naukri_rate = source_perf.loc['Naukri', 'Hire_Rate']
    ratio = linkedin_rate / naukri_rate if naukri_rate > 0 else 0
    print(f"\n✅ LinkedIn is {ratio:.1f}x better than Naukri ({linkedin_rate:.1f}% vs {naukri_rate:.1f}%)")

# Visualize
plt.figure(figsize=(12, 7))
colors_source = plt.cm.Greens(np.linspace(0.4, 0.9, len(source_perf)))
bars = plt.barh(source_perf.index, source_perf['Hire_Rate'], color=colors_source, edgecolor='darkgreen', linewidth=1.5)

plt.xlabel('Hire Rate (%)', fontsize=12, fontweight='bold')
plt.ylabel('Source', fontsize=12, fontweight='bold')
plt.title('Hire Rate by Recruiting Source', fontsize=16, fontweight='bold', pad=20)

# Add values on bars
for idx, (source, rate) in enumerate(source_perf['Hire_Rate'].items()):
    plt.text(rate + 0.3, idx, f"{rate:.1f}%", va='center', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('visualizations/source_effectiveness.png', dpi=300, bbox_inches='tight')
print("✅ Saved: visualizations/source_effectiveness.png")
plt.close()

# ======================================================================
# 4. SURVIVAL ANALYSIS (Time-to-Hire)
# ======================================================================
print("\n📊 Creating Visualization 4: Survival Analysis...")

try:
    from lifelines import KaplanMeierFitter
    
    # Prepare data for survival analysis
    hired_df = df[df['Stage'] == 'Hired'].copy()
    hired_df = hired_df.drop_duplicates(subset=['Applicant_ID'])
    
    if len(hired_df) > 0:
        kmf = KaplanMeierFitter()
        
        # Fit the model
        durations = hired_df['Days_Since_Application']
        event_observed = [1] * len(durations)  # All hired = event occurred
        
        kmf.fit(durations, event_observed, label='Time to Hire')
        
        # Plot survival curve
        plt.figure(figsize=(12, 7))
        kmf.plot_survival_function(ci_show=True)
        plt.title('Survival Curve: Time to Hire', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Days Since Application', fontsize=12, fontweight='bold')
        plt.ylabel('Probability of Not Being Hired Yet', fontsize=12, fontweight='bold')
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig('visualizations/survival_curve.png', dpi=300, bbox_inches='tight')
        print("✅ Saved: visualizations/survival_curve.png")
        plt.close()
        
        # Print median time to hire
        median_time = kmf.median_survival_time_
        print(f"\n⏱️  Median Time-to-Hire: {median_time:.1f} days")
    else:
        print("⚠️  No hired candidates found for survival analysis")
        
except ImportError:
    print("⚠️  Lifelines not installed. Skipping survival analysis.")
    print("   Install with: pip install lifelines")
    
    # Create alternative time-to-hire histogram
    hired_df = df[df['Stage'] == 'Hired'].copy()
    hired_df = hired_df.drop_duplicates(subset=['Applicant_ID'])
    
    if len(hired_df) > 0:
        plt.figure(figsize=(12, 7))
        plt.hist(hired_df['Days_Since_Application'], bins=20, color='steelblue', edgecolor='black', alpha=0.7)
        plt.xlabel('Days Since Application', fontsize=12, fontweight='bold')
        plt.ylabel('Number of Hires', fontsize=12, fontweight='bold')
        plt.title('Time-to-Hire Distribution', fontsize=16, fontweight='bold', pad=20)
        plt.axvline(hired_df['Days_Since_Application'].median(), color='red', linestyle='--', 
                   linewidth=2, label=f"Median: {hired_df['Days_Since_Application'].median():.1f} days")
        plt.legend(fontsize=11)
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig('visualizations/survival_curve.png', dpi=300, bbox_inches='tight')
        print("✅ Saved: visualizations/survival_curve.png (histogram version)")
        plt.close()

# ======================================================================
# 5. TIME-TO-HIRE BY SOURCE
# ======================================================================
print("\n📊 Creating Visualization 5: Time-to-Hire by Source...")

source_time = df.groupby(['Source', 'Applicant_ID'])['Days_Since_Application'].max().reset_index()

plt.figure(figsize=(14, 7))
sns.boxplot(data=source_time, x='Source', y='Days_Since_Application', 
            palette='Set2', linewidth=1.5)
plt.xticks(rotation=45, ha='right')
plt.ylabel('Days Since Application', fontsize=12, fontweight='bold')
plt.xlabel('Source', fontsize=12, fontweight='bold')
plt.title('Time-to-Hire Distribution by Source', fontsize=16, fontweight='bold', pad=20)
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('visualizations/time_to_hire_by_source.png', dpi=300, bbox_inches='tight')
print("✅ Saved: visualizations/time_to_hire_by_source.png")
plt.close()

# ======================================================================
# SUMMARY STATISTICS
# ======================================================================
print("\n" + "=" * 70)
print("📊 SUMMARY STATISTICS")
print("=" * 70)

total_applicants = df['Applicant_ID'].nunique()
total_hired = df[df['Stage'] == 'Hired']['Applicant_ID'].nunique()
hire_rate = (total_hired / total_applicants * 100)

print(f"\n📈 Overall Metrics:")
print(f"   Total Applicants: {total_applicants:,}")
print(f"   Total Hired: {total_hired:,}")
print(f"   Overall Hire Rate: {hire_rate:.1f}%")

hired_df = df[df['Stage'] == 'Hired']
if len(hired_df) > 0:
    print(f"   Average Time-to-Hire: {hired_df['Days_Since_Application'].mean():.1f} days")
    print(f"   Median Time-to-Hire: {hired_df['Days_Since_Application'].median():.1f} days")

print("\n" + "=" * 70)
print("✅ ALL VISUALIZATIONS CREATED SUCCESSFULLY!")
print("=" * 70)
print("\nGenerated files:")
print("   1. visualizations/recruitment_funnel.png")
print("   2. visualizations/drop_off_analysis.png")
print("   3. visualizations/source_effectiveness.png")
print("   4. visualizations/survival_curve.png")
print("   5. visualizations/time_to_hire_by_source.png")
print("\nNext steps:")
print("   1. Review visualizations")
print("   2. Create Power BI dashboard (see powerbi/POWERBI_SETUP_GUIDE.md)")
print("   3. Build Excel simulation (see excel/EXCEL_SIMULATION_GUIDE.md)")
print("=" * 70)
