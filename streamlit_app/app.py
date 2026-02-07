"""
Streamlit Interactive Dashboard for HR Recruitment Funnel Analytics
Run with: streamlit run streamlit_app/app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Page config
st.set_page_config(
    page_title="HR Recruitment Funnel Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1e3a8a;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f9ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3b82f6;
    }
    .insight-box {
        background-color: #fef3c7;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #f59e0b;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    """Load recruitment funnel data"""
    try:
        df = pd.read_csv('data/hr_recruitment_funnel.csv')
        df['Application_Date'] = pd.to_datetime(df['Application_Date'])
        df['Stage_Date'] = pd.to_datetime(df['Stage_Date'])
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Main app
def main():
    # Header
    st.markdown('<h1 class="main-header">🎯 HR Recruitment Funnel Analytics</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #6b7280; font-size: 1.1rem;">Enterprise-Grade ML-Powered Recruitment Intelligence Platform</p>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    if df is None:
        st.error("Failed to load data. Please check the data file.")
        return
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Date range filter
    min_date = df['Application_Date'].min()
    max_date = df['Application_Date'].max()
    date_range = st.sidebar.date_input(
        "Application Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Source filter
    sources = ['All'] + sorted(df['Source'].unique().tolist())
    selected_source = st.sidebar.selectbox("Recruiting Source", sources)
    
    # Department filter
    departments = ['All'] + sorted(df['Department'].unique().tolist())
    selected_dept = st.sidebar.selectbox("Department", departments)
    
    # Apply filters
    filtered_df = df.copy()
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['Application_Date'].dt.date >= date_range[0]) &
            (filtered_df['Application_Date'].dt.date <= date_range[1])
        ]
    if selected_source != 'All':
        filtered_df = filtered_df[filtered_df['Source'] == selected_source]
    if selected_dept != 'All':
        filtered_df = filtered_df[filtered_df['Department'] == selected_dept]
    
    # Key Metrics
    st.markdown("---")
    st.subheader("📊 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_applicants = filtered_df['Applicant_ID'].nunique()
    hired_count = filtered_df[filtered_df['Status'] == 'Hired']['Applicant_ID'].nunique()
    hire_rate = (hired_count / total_applicants * 100) if total_applicants > 0 else 0
    avg_time = filtered_df[filtered_df['Status'] == 'Hired']['Days_Since_Application'].mean()
    
    with col1:
        st.metric("Total Applicants", f"{total_applicants:,}")
    with col2:
        st.metric("Hired", f"{hired_count:,}")
    with col3:
        st.metric("Hire Rate", f"{hire_rate:.1f}%")
    with col4:
        st.metric("Avg Time-to-Hire", f"{avg_time:.0f} days" if not pd.isna(avg_time) else "N/A")
    
    # Recruitment Funnel
    st.markdown("---")
    st.subheader("📉 Recruitment Funnel")
    
    funnel_data = filtered_df.groupby(['Stage', 'Stage_Sequence']).agg({
        'Applicant_ID': 'nunique'
    }).reset_index().sort_values('Stage_Sequence')
    
    fig_funnel = go.Figure(go.Funnel(
        y=funnel_data['Stage'],
        x=funnel_data['Applicant_ID'],
        textinfo="value+percent initial",
        marker=dict(color=['#3b82f6', '#60a5fa', '#93c5fd', '#ef4444', '#bfdbfe', '#dbeafe', '#e0f2fe', '#059669'])
    ))
    
    fig_funnel.update_layout(
        title="Candidate Progression Through Hiring Stages",
        height=500
    )
    
    st.plotly_chart(fig_funnel, use_container_width=True)
    
    # Drop-off Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔴 Drop-off by Stage")
        
        dropoff_data = filtered_df.groupby('Stage').agg({
            'Applicant_ID': 'count',
            'Status': lambda x: (x == 'Rejected').sum()
        }).reset_index()
        dropoff_data.columns = ['Stage', 'Total', 'Rejected']
        dropoff_data['Drop_off_Rate'] = (dropoff_data['Rejected'] / dropoff_data['Total'] * 100)
        
        fig_dropoff = px.bar(
            dropoff_data,
            x='Stage',
            y='Drop_off_Rate',
            color='Drop_off_Rate',
            color_continuous_scale=['#10b981', '#f59e0b', '#ef4444'],
            title="Drop-off Rate by Stage"
        )
        
        st.plotly_chart(fig_dropoff, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Source Effectiveness")
        
        source_data = filtered_df.groupby('Source').agg({
            'Applicant_ID': 'nunique',
            'Status': lambda x: (x == 'Hired').sum()
        }).reset_index()
        source_data.columns = ['Source', 'Total', 'Hired']
        source_data['Hire_Rate'] = (source_data['Hired'] / source_data['Total'] * 100)
        source_data = source_data.sort_values('Hire_Rate', ascending=True)
        
        fig_source = px.bar(
            source_data,
            y='Source',
            x='Hire_Rate',
            orientation='h',
            color='Hire_Rate',
            color_continuous_scale='Greens',
            title="Hire Rate by Recruiting Source"
        )
        
        st.plotly_chart(fig_source, use_container_width=True)
    
    # Time-to-Hire Analysis
    st.markdown("---")
    st.subheader("⏱️ Time-to-Hire Analysis")
    
    hired_df = filtered_df[filtered_df['Status'] == 'Hired']
    
    if len(hired_df) > 0:
        fig_time = px.histogram(
            hired_df,
            x='Days_Since_Application',
            nbins=30,
            title="Distribution of Time-to-Hire",
            labels={'Days_Since_Application': 'Days', 'count': 'Number of Hires'},
            color_discrete_sequence=['#3b82f6']
        )
        
        fig_time.add_vline(
            x=hired_df['Days_Since_Application'].median(),
            line_dash="dash",
            line_color="red",
            annotation_text=f"Median: {hired_df['Days_Since_Application'].median():.0f} days"
        )
        
        st.plotly_chart(fig_time, use_container_width=True)
    
    # Key Insights
    st.markdown("---")
    st.subheader("💡 Key Insights")
    
    # Find biggest bottleneck
    if len(dropoff_data) > 0:
        max_dropoff_stage = dropoff_data.loc[dropoff_data['Drop_off_Rate'].idxmax()]
        
        st.markdown(f"""
        <div class="insight-box">
            <h4>🔴 Biggest Bottleneck: {max_dropoff_stage['Stage']}</h4>
            <p><strong>{max_dropoff_stage['Drop_off_Rate']:.1f}%</strong> of candidates drop off at this stage.</p>
            <p><strong>Recommendation:</strong> Focus improvement efforts here for maximum impact.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Best performing source
    if len(source_data) > 0:
        best_source = source_data.loc[source_data['Hire_Rate'].idxmax()]
        
        st.markdown(f"""
        <div class="insight-box">
            <h4>🎯 Best Performing Source: {best_source['Source']}</h4>
            <p><strong>{best_source['Hire_Rate']:.1f}%</strong> hire rate from {best_source['Total']} applicants.</p>
            <p><strong>Recommendation:</strong> Increase budget allocation to this source.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6b7280; padding: 2rem 0;">
        <p><strong>HR Recruitment Funnel Analytics</strong> | Built with Streamlit & Plotly</p>
        <p>👤 Divya Dhole | 🔗 <a href="https://github.com/Divyadhole/HR-Recruitment-Funnel">GitHub Repository</a></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
