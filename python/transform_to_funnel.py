"""
Transform HR Analytics Employee Attrition Data into Recruitment Funnel Data
This script adapts existing employee data to create a realistic recruitment funnel
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

print("=" * 70)
print("HR RECRUITMENT FUNNEL DATA TRANSFORMATION")
print("=" * 70)

# Load existing HR Analytics data
print("\n📂 Loading HR Analytics data...")
df_employees = pd.read_csv('data/HR_Analytics.csv')
print(f"✅ Loaded {len(df_employees)} employee records")

# Define recruitment stages (in order)
stages = [
    'Application Received',
    'Resume Screening',
    'HR Phone Screen',
    'Technical Round',
    'Manager Interview',
    'Final Interview',
    'Offer Extended',
    'Hired'
]

# Map departments to recruiting sources with different success rates
source_mapping = {
    'Sales': ['LinkedIn', 'Naukri', 'Company Website'],
    'Research & Development': ['LinkedIn', 'Campus Hiring', 'Employee Referral'],
    'Human Resources': ['LinkedIn', 'Naukri', 'Recruitment Agency']
}

# Source effectiveness (hire rate)
source_effectiveness = {
    'LinkedIn': 0.25,
    'Naukri': 0.12,
    'Employee Referral': 0.35,
    'Company Website': 0.18,
    'Campus Hiring': 0.22,
    'Recruitment Agency': 0.15
}

# Configuration
start_date = datetime(2024, 1, 1)
end_date = datetime(2025, 12, 31)

# Generate recruitment funnel data
print("\n🔄 Transforming employee data into recruitment funnel...")
funnel_data = []

for idx, employee in df_employees.iterrows():
    # Create applicant ID
    applicant_id = f"APP{1000 + idx}"
    
    # Assign source based on department
    dept = employee['Department']
    if dept in source_mapping:
        source = random.choice(source_mapping[dept])
    else:
        source = random.choice(list(source_effectiveness.keys()))
    
    # Use JobRole as the job they applied for
    job_role = employee['JobRole']
    
    # Generate application date
    application_date = start_date + timedelta(
        days=random.randint(0, (end_date - start_date).days)
    )
    
    # Determine if this applicant gets hired based on source effectiveness
    # Employees in dataset are "hired" so we'll create their journey
    # For variety, we'll make some fail at different stages
    
    conversion_prob = source_effectiveness[source]
    gets_hired = random.random() < (conversion_prob * 2.5)  # Adjust to get realistic numbers
    
    current_date = application_date
    stage_sequence = 1
    
    # Simulate progression through stages
    for stage_idx, stage in enumerate(stages):
        # Determine if applicant passes this stage
        if stage == 'Application Received':
            pass_stage = True  # Everyone starts here
        elif stage == 'Resume Screening':
            pass_stage = random.random() < 0.70  # 70% pass
        elif stage == 'HR Phone Screen':
            pass_stage = random.random() < 0.75  # 75% pass
        elif stage == 'Technical Round':
            # This is where we want 27% drop-off
            pass_stage = random.random() < 0.55  # 55% pass (45% drop)
        elif stage == 'Manager Interview':
            pass_stage = random.random() < 0.70  # 70% pass
        elif stage == 'Final Interview':
            pass_stage = random.random() < 0.80  # 80% pass
        elif stage == 'Offer Extended':
            pass_stage = random.random() < 0.90  # 90% accept
        elif stage == 'Hired':
            pass_stage = gets_hired
        
        if pass_stage:
            # Time between stages (in days)
            if stage_idx == 0:
                days_to_next = 0
            else:
                days_to_next = random.randint(3, 10)
            
            current_date += timedelta(days=days_to_next)
            
            funnel_data.append({
                'Applicant_ID': applicant_id,
                'Source': source,
                'Job_Role': job_role,
                'Department': dept,
                'Application_Date': application_date.strftime('%Y-%m-%d'),
                'Stage': stage,
                'Stage_Sequence': stage_sequence,
                'Stage_Date': current_date.strftime('%Y-%m-%d'),
                'Status': 'Passed' if stage != stages[-1] else 'Hired',
                'Days_Since_Application': (current_date - application_date).days,
                # Additional fields from original data for enrichment
                'Age': employee['Age'],
                'Gender': employee['Gender'],
                'Education': employee['Education'],
                'EducationField': employee['EducationField']
            })
            stage_sequence += 1
        else:
            # Applicant dropped off at this stage
            funnel_data.append({
                'Applicant_ID': applicant_id,
                'Source': source,
                'Job_Role': job_role,
                'Department': dept,
                'Application_Date': application_date.strftime('%Y-%m-%d'),
                'Stage': stage,
                'Stage_Sequence': stage_sequence,
                'Stage_Date': current_date.strftime('%Y-%m-%d'),
                'Status': 'Rejected',
                'Days_Since_Application': (current_date - application_date).days,
                'Age': employee['Age'],
                'Gender': employee['Gender'],
                'Education': employee['Education'],
                'EducationField': employee['EducationField']
            })
            break  # Stop progression

# Create DataFrame
df_funnel = pd.DataFrame(funnel_data)

# Save to CSV
output_file = 'data/hr_recruitment_funnel.csv'
df_funnel.to_csv(output_file, index=False)
print(f"✅ Saved recruitment funnel data to: {output_file}")

# Generate comprehensive statistics
print("\n" + "=" * 70)
print("📊 RECRUITMENT FUNNEL STATISTICS")
print("=" * 70)

print(f"\n📈 Overall Metrics:")
print(f"   Total Records: {len(df_funnel):,}")
print(f"   Unique Applicants: {df_funnel['Applicant_ID'].nunique():,}")
print(f"   Date Range: {df_funnel['Application_Date'].min()} to {df_funnel['Application_Date'].max()}")

print(f"\n👥 Applicants by Source:")
source_stats = df_funnel.groupby('Source')['Applicant_ID'].nunique().sort_values(ascending=False)
for source, count in source_stats.items():
    print(f"   {source:.<25} {count:>4} applicants")

print(f"\n📊 Applicants by Stage:")
stage_stats = df_funnel.groupby(['Stage', 'Stage_Sequence'])['Applicant_ID'].nunique().sort_values(ascending=False)
for (stage, seq), count in stage_stats.items():
    print(f"   {seq}. {stage:.<30} {count:>4} applicants")

print(f"\n🎯 Hire Rate by Source:")
hired_by_source = df_funnel[df_funnel['Stage'] == 'Hired'].groupby('Source')['Applicant_ID'].nunique()
total_by_source = df_funnel.groupby('Source')['Applicant_ID'].nunique()
hire_rates = (hired_by_source / total_by_source * 100).sort_values(ascending=False)
for source, rate in hire_rates.items():
    print(f"   {source:.<25} {rate:>5.1f}%")

# Calculate LinkedIn vs Naukri ratio
if 'LinkedIn' in hire_rates.index and 'Naukri' in hire_rates.index:
    ratio = hire_rates['LinkedIn'] / hire_rates['Naukri']
    print(f"\n   ⭐ LinkedIn is {ratio:.1f}x better than Naukri!")

# Calculate drop-off rates
print(f"\n📉 Drop-off Rates by Stage:")
stage_counts = df_funnel.groupby(['Stage', 'Stage_Sequence'])['Applicant_ID'].nunique().reset_index()
stage_counts = stage_counts.sort_values('Stage_Sequence')
stage_counts.columns = ['Stage', 'Sequence', 'Applicants']

for i in range(len(stage_counts) - 1):
    current = stage_counts.iloc[i]
    next_stage = stage_counts.iloc[i + 1]
    drop_off = ((current['Applicants'] - next_stage['Applicants']) / current['Applicants']) * 100
    print(f"   {current['Stage']:.<30} {drop_off:>5.1f}% drop-off")

# Find highest drop-off
max_drop_idx = 0
max_drop = 0
for i in range(len(stage_counts) - 1):
    current = stage_counts.iloc[i]
    next_stage = stage_counts.iloc[i + 1]
    drop_off = ((current['Applicants'] - next_stage['Applicants']) / current['Applicants']) * 100
    if drop_off > max_drop:
        max_drop = drop_off
        max_drop_idx = i

if max_drop_idx < len(stage_counts) - 1:
    print(f"\n   ⚠️  HIGHEST DROP-OFF: {stage_counts.iloc[max_drop_idx]['Stage']} ({max_drop:.1f}%)")

# Time to hire statistics
hired_applicants = df_funnel[df_funnel['Stage'] == 'Hired']
if len(hired_applicants) > 0:
    avg_time = hired_applicants['Days_Since_Application'].mean()
    median_time = hired_applicants['Days_Since_Application'].median()
    print(f"\n⏱️  Time-to-Hire:")
    print(f"   Average: {avg_time:.1f} days")
    print(f"   Median: {median_time:.1f} days")

# Create summary Excel file
print(f"\n📑 Creating summary Excel file...")
with pd.ExcelWriter('data/recruitment_summary.xlsx', engine='openpyxl') as writer:
    # Overall summary
    summary_df = pd.DataFrame({
        'Metric': ['Total Applicants', 'Total Hired', 'Overall Hire Rate (%)', 
                   'Avg Time to Hire (days)', 'Median Time to Hire (days)'],
        'Value': [
            df_funnel['Applicant_ID'].nunique(),
            hired_applicants['Applicant_ID'].nunique(),
            (hired_applicants['Applicant_ID'].nunique() / df_funnel['Applicant_ID'].nunique() * 100),
            avg_time if len(hired_applicants) > 0 else 0,
            median_time if len(hired_applicants) > 0 else 0
        ]
    })
    summary_df.to_excel(writer, sheet_name='Overall Summary', index=False)
    
    # Source effectiveness
    source_summary = pd.DataFrame({
        'Source': total_by_source.index,
        'Total Applicants': total_by_source.values,
        'Hired': [hired_by_source.get(s, 0) for s in total_by_source.index],
        'Hire Rate (%)': [hire_rates.get(s, 0) for s in total_by_source.index]
    }).sort_values('Hire Rate (%)', ascending=False)
    source_summary.to_excel(writer, sheet_name='Source Effectiveness', index=False)
    
    # Stage funnel
    stage_counts.to_excel(writer, sheet_name='Stage Funnel', index=False)
    
    # Sample data
    df_funnel.head(100).to_excel(writer, sheet_name='Sample Data', index=False)

print(f"✅ Saved summary to: data/recruitment_summary.xlsx")

print("\n" + "=" * 70)
print("✅ TRANSFORMATION COMPLETE!")
print("=" * 70)
print(f"\nNext steps:")
print(f"1. Review the data: data/hr_recruitment_funnel.csv")
print(f"2. Check the summary: data/recruitment_summary.xlsx")
print(f"3. Run SQL analysis: python python/load_to_sql.py")
print(f"4. Generate visualizations: python python/survival_analysis.py")
print("=" * 70)
