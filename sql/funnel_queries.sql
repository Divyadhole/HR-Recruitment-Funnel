-- ======================================================================
-- HR RECRUITMENT FUNNEL - SQL ANALYSIS QUERIES
-- ======================================================================
-- This file contains all SQL queries for analyzing the recruitment funnel
-- Run with: sqlite3 recruitment.db < sql/funnel_queries.sql
-- ======================================================================

.mode column
.headers on
.width 30 15 15 15

-- ======================================================================
-- QUERY 1: Funnel Conversion Rates by Source
-- ======================================================================
-- Calculate stage-by-stage conversion rates using window functions
-- Shows how many applicants progress from each stage to the next

.print ""
.print "======================================================================"
.print "QUERY 1: FUNNEL CONVERSION RATES BY SOURCE"
.print "======================================================================"
.print ""

WITH stage_counts AS (
    SELECT 
        Stage,
        Source,
        Stage_Sequence,
        COUNT(DISTINCT Applicant_ID) as applicants
    FROM applicant_stages
    GROUP BY Stage, Source, Stage_Sequence
)
SELECT 
    Source,
    Stage,
    applicants,
    ROUND(
        applicants * 100.0 / 
        LAG(applicants) OVER (
            PARTITION BY Source 
            ORDER BY Stage_Sequence
        ), 
        2
    ) as conversion_rate_pct,
    ROUND(
        100.0 - (applicants * 100.0 / 
        LAG(applicants) OVER (
            PARTITION BY Source 
            ORDER BY Stage_Sequence
        )), 
        2
    ) as drop_off_rate_pct
FROM stage_counts
ORDER BY Source, Stage_Sequence;

-- ======================================================================
-- QUERY 2: Identify Highest Drop-off Stage
-- ======================================================================
-- Find which recruitment stage has the highest rejection rate

.print ""
.print "======================================================================"
.print "QUERY 2: HIGHEST DROP-OFF STAGES"
.print "======================================================================"
.print ""

SELECT 
    Stage,
    Stage_Sequence,
    COUNT(DISTINCT Applicant_ID) as total_applicants,
    COUNT(DISTINCT CASE WHEN Status = 'Rejected' THEN Applicant_ID END) as rejected,
    ROUND(
        COUNT(DISTINCT CASE WHEN Status = 'Rejected' THEN Applicant_ID END) * 100.0 / 
        COUNT(DISTINCT Applicant_ID), 
        2
    ) as rejection_rate_pct
FROM applicant_stages
GROUP BY Stage, Stage_Sequence
ORDER BY rejection_rate_pct DESC
LIMIT 10;

-- ======================================================================
-- QUERY 3: Source Effectiveness Comparison
-- ======================================================================
-- Compare recruiting sources by hire rate and time-to-hire
-- Shows LinkedIn vs Naukri performance

.print ""
.print "======================================================================"
.print "QUERY 3: SOURCE EFFECTIVENESS (LinkedIn 2.1x Better Analysis)"
.print "======================================================================"
.print ""

WITH source_metrics AS (
    SELECT 
        Source,
        COUNT(DISTINCT Applicant_ID) as total_applicants,
        COUNT(DISTINCT CASE 
            WHEN Stage = 'Hired' AND Status = 'Hired' 
            THEN Applicant_ID 
        END) as hired_count,
        ROUND(AVG(CASE 
            WHEN Stage = 'Hired' 
            THEN Days_Since_Application 
        END), 1) as avg_time_to_hire
    FROM applicant_stages
    GROUP BY Source
)
SELECT 
    Source,
    total_applicants,
    hired_count,
    ROUND(hired_count * 100.0 / total_applicants, 2) as hire_rate_pct,
    avg_time_to_hire,
    ROUND(
        (hired_count * 100.0 / total_applicants) / 
        (SELECT hired_count * 100.0 / total_applicants 
         FROM source_metrics 
         WHERE Source = 'Naukri'),
        2
    ) as vs_naukri_multiplier
FROM source_metrics
ORDER BY hire_rate_pct DESC;

-- ======================================================================
-- QUERY 4: Stage-by-Stage Funnel with Retention Rates
-- ======================================================================
-- Classic funnel view showing progression through all stages

.print ""
.print "======================================================================"
.print "QUERY 4: STAGE-BY-STAGE FUNNEL"
.print "======================================================================"
.print ""

WITH funnel AS (
    SELECT 
        Stage,
        Stage_Sequence,
        COUNT(DISTINCT Applicant_ID) as applicants
    FROM applicant_stages
    GROUP BY Stage, Stage_Sequence
)
SELECT 
    Stage_Sequence,
    Stage,
    applicants,
    LAG(applicants) OVER (ORDER BY Stage_Sequence) as previous_stage,
    ROUND(
        applicants * 100.0 / 
        LAG(applicants) OVER (ORDER BY Stage_Sequence), 
        2
    ) as retention_rate_pct,
    ROUND(
        100.0 - (applicants * 100.0 / 
        LAG(applicants) OVER (ORDER BY Stage_Sequence)), 
        2
    ) as drop_off_pct
FROM funnel
ORDER BY Stage_Sequence;

-- ======================================================================
-- QUERY 5: Time-to-Hire Distribution
-- ======================================================================
-- Analyze how long it takes to hire candidates

.print ""
.print "======================================================================"
.print "QUERY 5: TIME-TO-HIRE DISTRIBUTION"
.print "======================================================================"
.print ""

SELECT 
    CASE 
        WHEN Days_Since_Application <= 30 THEN '0-30 days'
        WHEN Days_Since_Application <= 60 THEN '31-60 days'
        WHEN Days_Since_Application <= 90 THEN '61-90 days'
        ELSE '90+ days'
    END as time_bucket,
    COUNT(DISTINCT Applicant_ID) as hired_count,
    ROUND(AVG(Days_Since_Application), 1) as avg_days
FROM applicant_stages
WHERE Stage = 'Hired' AND Status = 'Hired'
GROUP BY time_bucket
ORDER BY 
    CASE time_bucket
        WHEN '0-30 days' THEN 1
        WHEN '31-60 days' THEN 2
        WHEN '61-90 days' THEN 3
        ELSE 4
    END;

-- ======================================================================
-- QUERY 6: Department-wise Hiring Performance
-- ======================================================================

.print ""
.print "======================================================================"
.print "QUERY 6: DEPARTMENT-WISE HIRING PERFORMANCE"
.print "======================================================================"
.print ""

SELECT 
    Department,
    COUNT(DISTINCT Applicant_ID) as total_applicants,
    COUNT(DISTINCT CASE 
        WHEN Stage = 'Hired' AND Status = 'Hired' 
        THEN Applicant_ID 
    END) as hired,
    ROUND(
        COUNT(DISTINCT CASE 
            WHEN Stage = 'Hired' AND Status = 'Hired' 
            THEN Applicant_ID 
        END) * 100.0 / COUNT(DISTINCT Applicant_ID), 
        2
    ) as hire_rate_pct
FROM applicant_stages
GROUP BY Department
ORDER BY hire_rate_pct DESC;

-- ======================================================================
-- QUERY 7: Gender Diversity in Hiring
-- ======================================================================

.print ""
.print "======================================================================"
.print "QUERY 7: GENDER DIVERSITY IN HIRING"
.print "======================================================================"
.print ""

SELECT 
    Gender,
    COUNT(DISTINCT Applicant_ID) as total_applicants,
    COUNT(DISTINCT CASE 
        WHEN Stage = 'Hired' AND Status = 'Hired' 
        THEN Applicant_ID 
    END) as hired,
    ROUND(
        COUNT(DISTINCT CASE 
            WHEN Stage = 'Hired' AND Status = 'Hired' 
            THEN Applicant_ID 
        END) * 100.0 / COUNT(DISTINCT Applicant_ID), 
        2
    ) as hire_rate_pct
FROM applicant_stages
GROUP BY Gender
ORDER BY hired DESC;

.print ""
.print "======================================================================"
.print "SQL ANALYSIS COMPLETE"
.print "======================================================================"
