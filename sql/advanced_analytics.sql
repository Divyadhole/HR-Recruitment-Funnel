"""
Advanced SQL Analytics Queries
Includes cohort analysis, statistical tests, and advanced window functions
"""

-- ============================================================================
-- 1. COHORT ANALYSIS - Track applicant groups over time
-- ============================================================================

-- Cohort by application month
WITH monthly_cohorts AS (
    SELECT 
        Applicant_ID,
        Source,
        strftime('%Y-%m', Application_Date) as cohort_month,
        Stage,
        Status,
        Stage_Sequence
    FROM applicant_stages
),
cohort_progression AS (
    SELECT 
        cohort_month,
        Source,
        COUNT(DISTINCT Applicant_ID) as total_applicants,
        SUM(CASE WHEN Status = 'Hired' THEN 1 ELSE 0 END) as hired_count,
        ROUND(100.0 * SUM(CASE WHEN Status = 'Hired' THEN 1 ELSE 0 END) / COUNT(DISTINCT Applicant_ID), 2) as hire_rate
    FROM monthly_cohorts
    GROUP BY cohort_month, Source
    ORDER BY cohort_month, hire_rate DESC
)
SELECT * FROM cohort_progression;

-- ============================================================================
-- 2. RETENTION CURVES BY SOURCE
-- ============================================================================

WITH stage_retention AS (
    SELECT 
        Source,
        Stage,
        Stage_Sequence,
        COUNT(DISTINCT Applicant_ID) as applicants_at_stage,
        FIRST_VALUE(COUNT(DISTINCT Applicant_ID)) OVER (
            PARTITION BY Source 
            ORDER BY Stage_Sequence
        ) as initial_applicants
    FROM applicant_stages
    GROUP BY Source, Stage, Stage_Sequence
)
SELECT 
    Source,
    Stage,
    Stage_Sequence,
    applicants_at_stage,
    initial_applicants,
    ROUND(100.0 * applicants_at_stage / initial_applicants, 2) as retention_rate,
    ROUND(100.0 * (initial_applicants - applicants_at_stage) / initial_applicants, 2) as cumulative_drop_off
FROM stage_retention
ORDER BY Source, Stage_Sequence;

-- ============================================================================
-- 3. PERCENTILE ANALYSIS USING NTILE
-- ============================================================================

-- Divide applicants into quartiles based on time-to-hire
WITH time_quartiles AS (
    SELECT 
        Applicant_ID,
        Source,
        Days_Since_Application,
        Status,
        NTILE(4) OVER (ORDER BY Days_Since_Application) as time_quartile
    FROM applicant_stages
    WHERE Status = 'Hired'
)
SELECT 
    time_quartile,
    CASE 
        WHEN time_quartile = 1 THEN 'Fastest (Q1)'
        WHEN time_quartile = 2 THEN 'Fast (Q2)'
        WHEN time_quartile = 3 THEN 'Slow (Q3)'
        ELSE 'Slowest (Q4)'
    END as quartile_label,
    COUNT(*) as hired_count,
    ROUND(AVG(Days_Since_Application), 1) as avg_days,
    MIN(Days_Since_Application) as min_days,
    MAX(Days_Since_Application) as max_days
FROM time_quartiles
GROUP BY time_quartile
ORDER BY time_quartile;

-- ============================================================================
-- 4. PERCENT_RANK - Identify top and bottom performers
-- ============================================================================

WITH source_performance AS (
    SELECT 
        Source,
        COUNT(DISTINCT Applicant_ID) as total_applicants,
        SUM(CASE WHEN Status = 'Hired' THEN 1 ELSE 0 END) as hired_count,
        ROUND(100.0 * SUM(CASE WHEN Status = 'Hired' THEN 1 ELSE 0 END) / COUNT(DISTINCT Applicant_ID), 2) as hire_rate
    FROM applicant_stages
    GROUP BY Source
),
ranked_sources AS (
    SELECT 
        Source,
        total_applicants,
        hired_count,
        hire_rate,
        PERCENT_RANK() OVER (ORDER BY hire_rate) as percentile_rank
    FROM source_performance
)
SELECT 
    Source,
    total_applicants,
    hired_count,
    hire_rate,
    ROUND(percentile_rank * 100, 1) as performance_percentile,
    CASE 
        WHEN percentile_rank >= 0.75 THEN 'Top Performer'
        WHEN percentile_rank >= 0.50 THEN 'Above Average'
        WHEN percentile_rank >= 0.25 THEN 'Below Average'
        ELSE 'Bottom Performer'
    END as performance_tier
FROM ranked_sources
ORDER BY hire_rate DESC;

-- ============================================================================
-- 5. MOVING AVERAGES - Time series trend analysis
-- ============================================================================

WITH daily_applications AS (
    SELECT 
        DATE(Application_Date) as app_date,
        COUNT(DISTINCT Applicant_ID) as daily_applicants
    FROM applicant_stages
    WHERE Stage = 'Application Received'
    GROUP BY DATE(Application_Date)
),
moving_avg AS (
    SELECT 
        app_date,
        daily_applicants,
        AVG(daily_applicants) OVER (
            ORDER BY app_date 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) as seven_day_avg,
        AVG(daily_applicants) OVER (
            ORDER BY app_date 
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) as thirty_day_avg
    FROM daily_applications
)
SELECT 
    app_date,
    daily_applicants,
    ROUND(seven_day_avg, 1) as seven_day_moving_avg,
    ROUND(thirty_day_avg, 1) as thirty_day_moving_avg,
    CASE 
        WHEN daily_applicants > seven_day_avg * 1.2 THEN 'High Volume'
        WHEN daily_applicants < seven_day_avg * 0.8 THEN 'Low Volume'
        ELSE 'Normal'
    END as volume_status
FROM moving_avg
ORDER BY app_date DESC
LIMIT 30;

-- ============================================================================
-- 6. CANDIDATE JOURNEY ANALYSIS - Path through stages
-- ============================================================================

WITH candidate_paths AS (
    SELECT 
        Applicant_ID,
        Source,
        GROUP_CONCAT(Stage, ' → ') as journey_path,
        COUNT(*) as stages_completed,
        MAX(CASE WHEN Status = 'Hired' THEN 1 ELSE 0 END) as was_hired
    FROM applicant_stages
    GROUP BY Applicant_ID, Source
)
SELECT 
    journey_path,
    COUNT(*) as candidate_count,
    SUM(was_hired) as hired_count,
    ROUND(100.0 * SUM(was_hired) / COUNT(*), 2) as success_rate,
    ROUND(AVG(stages_completed), 1) as avg_stages
FROM candidate_paths
GROUP BY journey_path
HAVING COUNT(*) >= 5  -- Only show common paths
ORDER BY candidate_count DESC
LIMIT 20;

-- ============================================================================
-- 7. DEPARTMENT COMPARISON WITH STATISTICAL SIGNIFICANCE
-- ============================================================================

-- Chi-square test preparation data
WITH dept_stats AS (
    SELECT 
        Department,
        COUNT(DISTINCT Applicant_ID) as total_applicants,
        SUM(CASE WHEN Status = 'Hired' THEN 1 ELSE 0 END) as hired,
        SUM(CASE WHEN Status = 'Rejected' THEN 1 ELSE 0 END) as rejected
    FROM applicant_stages
    GROUP BY Department
),
overall_stats AS (
    SELECT 
        SUM(total_applicants) as grand_total,
        SUM(hired) as total_hired,
        SUM(rejected) as total_rejected,
        ROUND(100.0 * SUM(hired) / SUM(total_applicants), 2) as overall_hire_rate
    FROM dept_stats
)
SELECT 
    d.Department,
    d.total_applicants,
    d.hired,
    d.rejected,
    ROUND(100.0 * d.hired / d.total_applicants, 2) as dept_hire_rate,
    o.overall_hire_rate,
    ROUND(100.0 * d.hired / d.total_applicants - o.overall_hire_rate, 2) as variance_from_avg,
    CASE 
        WHEN 100.0 * d.hired / d.total_applicants > o.overall_hire_rate * 1.1 THEN 'Significantly Above'
        WHEN 100.0 * d.hired / d.total_applicants < o.overall_hire_rate * 0.9 THEN 'Significantly Below'
        ELSE 'Within Expected Range'
    END as statistical_assessment
FROM dept_stats d
CROSS JOIN overall_stats o
ORDER BY dept_hire_rate DESC;

-- ============================================================================
-- 8. TIME-BASED COHORT RETENTION
-- ============================================================================

WITH applicant_cohorts AS (
    SELECT 
        Applicant_ID,
        MIN(DATE(Application_Date)) as cohort_date,
        MAX(Stage_Sequence) as max_stage_reached,
        MAX(CASE WHEN Status = 'Hired' THEN 1 ELSE 0 END) as was_hired
    FROM applicant_stages
    GROUP BY Applicant_ID
),
cohort_summary AS (
    SELECT 
        strftime('%Y-%m', cohort_date) as cohort_month,
        COUNT(*) as cohort_size,
        SUM(CASE WHEN max_stage_reached >= 3 THEN 1 ELSE 0 END) as reached_technical,
        SUM(CASE WHEN max_stage_reached >= 5 THEN 1 ELSE 0 END) as reached_final,
        SUM(was_hired) as hired
    FROM applicant_cohorts
    GROUP BY strftime('%Y-%m', cohort_date)
)
SELECT 
    cohort_month,
    cohort_size,
    reached_technical,
    ROUND(100.0 * reached_technical / cohort_size, 2) as pct_to_technical,
    reached_final,
    ROUND(100.0 * reached_final / cohort_size, 2) as pct_to_final,
    hired,
    ROUND(100.0 * hired / cohort_size, 2) as hire_rate
FROM cohort_summary
ORDER BY cohort_month;
