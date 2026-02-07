# Power BI Dashboard Setup Guide

This guide provides step-by-step instructions for creating an interactive HR Recruitment Funnel dashboard in Power BI Desktop.

## Prerequisites
- Power BI Desktop (Download from: https://powerbi.microsoft.com/desktop/)
- Data file: `data/hr_recruitment_funnel.csv`

---

## Step 1: Import Data

1. Open Power BI Desktop
2. Click **Get Data** → **Text/CSV**
3. Select `data/hr_recruitment_funnel.csv`
4. Click **Load**

---

## Step 2: Create DAX Measures

Go to **Modeling** tab → **New Measure** and create the following:

### Total Applicants
```dax
Total Applicants = DISTINCTCOUNT(applicant_stages[Applicant_ID])
```

### Total Hired
```dax
Total Hired = 
CALCULATE(
    DISTINCTCOUNT(applicant_stages[Applicant_ID]),
    applicant_stages[Stage] = "Hired",
    applicant_stages[Status] = "Hired"
)
```

### Hire Rate
```dax
Hire Rate = 
DIVIDE([Total Hired], [Total Applicants], 0) * 100
```

### Average Time to Hire
```dax
Avg Time to Hire = 
CALCULATE(
    AVERAGE(applicant_stages[Days_Since_Application]),
    applicant_stages[Stage] = "Hired"
)
```

### Drop-off Rate (by Stage)
```dax
Drop Off Rate = 
VAR CurrentStageCount = DISTINCTCOUNT(applicant_stages[Applicant_ID])
VAR PreviousStageCount = 
    CALCULATE(
        DISTINCTCOUNT(applicant_stages[Applicant_ID]),
        FILTER(
            ALL(applicant_stages),
            applicant_stages[Stage_Sequence] = EARLIER(applicant_stages[Stage_Sequence]) - 1
        )
    )
RETURN
DIVIDE(PreviousStageCount - CurrentStageCount, PreviousStageCount, 0) * 100
```

---

## Step 3: Create Visualizations

### 1. KPI Cards (Top Row)
Create 4 **Card** visuals:
- **Card 1**: Total Applicants measure
- **Card 2**: Total Hired measure  
- **Card 3**: Hire Rate measure (format as percentage)
- **Card 4**: Avg Time to Hire measure

**Formatting**:
- Font size: 24pt for value
- Add data labels
- Background color: Light blue

---

### 2. Sankey Diagram (Main Visual) ⭐
**This is the hero visual showing candidate flow!**

1. Click **Get more visuals** (three dots in Visualizations pane)
2. Search for "Sankey Diagram"
3. Install the visual
4. Add to canvas
5. Configure:
   - **Source**: Source field
   - **Destination**: Stage field
   - **Weight**: Count of Applicant_ID

**What it shows**: How candidates flow from each recruiting source through each stage!

---

### 3. Funnel Chart
1. Select **Funnel** visual
2. Configure:
   - **Category**: Stage (sorted by Stage_Sequence)
   - **Values**: Count of Applicant_ID

**Formatting**:
- Sort by Stage_Sequence ascending
- Show data labels

---

### 4. Gauge Chart (Time-to-Hire vs Target)
1. Select **Gauge** visual
2. Configure:
   - **Value**: Avg Time to Hire measure
   - **Target**: 60 (manual entry for target days)
   - **Maximum**: 90

**Formatting**:
- Target color: Red
- Value color: Green if below target

---

### 5. Decomposition Tree (Drop-off Analysis)
1. Select **Decomposition Tree** visual
2. Configure:
   - **Analyze**: Applicant_ID (Count)
   - **Explain by**: Source → Stage → Job_Role → Department

**Usage**: Click on any node to drill down and find where candidates drop off most!

---

### 6. Column Chart (Source Comparison)
1. Select **Clustered Column Chart**
2. Configure:
   - **X-axis**: Source
   - **Y-axis**: Hire Rate measure
   - **Data labels**: On

**Formatting**:
- Sort by Hire Rate descending
- Color by Source

---

### 7. Line Chart (Stage Progression)
1. Select **Line Chart**
2. Configure:
   - **X-axis**: Stage (sorted by Stage_Sequence)
   - **Y-axis**: Count of Applicant_ID
   - **Legend**: Source

**What it shows**: How each source performs across stages

---

## Step 4: Dashboard Layout

Arrange visuals in this layout:

```
┌─────────────────────────────────────────────────────────────┐
│        HR Recruitment Funnel Dashboard                      │
├──────────┬──────────┬──────────┬───────────────────────────┤
│  1,480   │   231    │  15.6%   │      43 days             │
│Applicants│  Hired   │Hire Rate │  Time-to-Hire            │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│           SANKEY DIAGRAM (Source → Stage Flow)              │
│                  [Main Visual - Large]                       │
│                                                              │
├───────────────────────┬──────────────────────────────────────┤
│                       │                                      │
│   Funnel Chart        │   Gauge (Time-to-Hire)              │
│   (Stage Drop-off)    │   Target: 60 days                   │
│                       │                                      │
├───────────────────────┴──────────────────────────────────────┤
│                                                              │
│   Source Effectiveness (Column Chart)                       │
│   Company Website: 19% | Campus: 16% | LinkedIn: 16%       │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Step 5: Add Slicers (Filters)

Add these slicers for interactivity:
1. **Date Range**: Application_Date
2. **Department**: Department field
3. **Source**: Source field
4. **Gender**: Gender field

---

## Step 6: Format Dashboard

1. **Theme**: Apply a professional theme (Format → Themes → Executive)
2. **Background**: Light gray (#F5F5F5)
3. **Title**: Add text box with "HR Recruitment Funnel Analytics"
4. **Borders**: Add subtle borders to visuals

---

## Step 7: Save and Publish

1. **Save**: File → Save As → `powerbi/HR_Recruitment_Dashboard.pbix`
2. **Publish** (Optional):
   - Sign in to Power BI Service
   - Click **Publish**
   - Select workspace
   - Share link with stakeholders

---

## Key Insights to Highlight

When presenting this dashboard:

1. **45.4% drop-off at Technical Round** - Highest bottleneck
2. **Company Website has highest hire rate (19.4%)**
3. **Average time-to-hire: 43 days** (below 60-day target ✅)
4. **Sankey diagram shows** exact candidate flow from source to hire

---

## Tips for Presentation

- Use the Sankey diagram to tell the story of candidate journey
- Click on Technical Round in Decomposition Tree to show which sources/roles drop most
- Filter by specific sources to compare performance
- Highlight that we're beating the 60-day time-to-hire target

---

## Troubleshooting

**Issue**: Sankey diagram not available
- **Solution**: Install from AppSource (Get more visuals)

**Issue**: Measures showing blank
- **Solution**: Check that field names match exactly (case-sensitive)

**Issue**: Funnel not sorting correctly
- **Solution**: Sort by Stage_Sequence field, not Stage name

---

## Next Steps

1. Create the dashboard following this guide
2. Take screenshots for documentation
3. Export to PDF for sharing
4. Consider publishing to Power BI Service for live updates
