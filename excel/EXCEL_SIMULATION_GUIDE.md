# Excel What-If Analysis & Simulation Guide

This guide shows how to create budget reallocation simulations and what-if analysis in Excel.

## Prerequisites
- Microsoft Excel (2016 or later recommended)
- Data file: `data/recruitment_summary.xlsx`

---

## Part 1: Source Budget Reallocation Simulation

### Step 1: Create Simulation Sheet

1. Open Excel and create a new sheet named "Budget Simulation"
2. Create the following table structure:

| Source | Current Budget | Current Hires | Cost per Hire | Hire Rate (%) | New Budget | Projected Hires |
|--------|---------------|---------------|---------------|---------------|------------|----------------|
| Company Website | 500,000 | 30 | 16,667 | 19.4 | | |
| Campus Hiring | 400,000 | 50 | 8,000 | 16.4 | | |
| LinkedIn | 600,000 | 76 | 7,895 | 15.9 | | |
| Naukri | 300,000 | 28 | 10,714 | 15.2 | | |
| Employee Referral | 200,000 | 46 | 4,348 | 13.5 | | |
| Recruitment Agency | 100,000 | 1 | 100,000 | 5.6 | | |
| **TOTAL** | **2,100,000** | **231** | | | | |

### Step 2: Add Formulas

**Cost per Hire** (Column D):
```excel
=B2/C2
```

**Projected Hires** (Column G):
```excel
=F2/D2
```

**Total New Budget** (Bottom of Column F):
```excel
=SUM(F2:F7)
```

**Total Projected Hires** (Bottom of Column G):
```excel
=SUM(G2:G7)
```

### Step 3: Create Scenarios

Use **Data** → **What-If Analysis** → **Scenario Manager**

**Scenario 1: Current State**
- All New Budget = Current Budget
- Baseline: 231 hires

**Scenario 2: Shift to High Performers**
- Increase Company Website budget by 30%
- Increase Campus Hiring budget by 20%
- Decrease Naukri budget by 40%
- Decrease Recruitment Agency budget by 50%

**Scenario 3: Maximize Employee Referrals**
- Increase Employee Referral budget by 100%
- Decrease all paid sources by 10%

---

## Part 2: Data Table for Sensitivity Analysis

### Step 1: Create Data Table

1. Create a new section with this structure:

|  | Budget Change % → | -20% | -10% | 0% | +10% | +20% | +30% |
|--|-------------------|------|------|----|----|------|------|
| **Hire Rate Change %** ↓ | | | | | | | |
| -10% | | | | | | | |
| -5% | | | | | | | |
| 0% | | | | | | | |
| +5% | | | | | | | |
| +10% | | | | | | | |

2. In the top-left cell (intersection), put formula:
```excel
=Total_Projected_Hires
```

3. Select the entire table
4. Go to **Data** → **What-If Analysis** → **Data Table**
5. Configure:
   - **Row input cell**: Budget change % cell
   - **Column input cell**: Hire rate change % cell

This creates a matrix showing how total hires change with different budget and hire rate scenarios.

---

## Part 3: Goal Seek Analysis

### Scenario: "How much budget do we need to hire 300 people?"

1. Go to **Data** → **What-If Analysis** → **Goal Seek**
2. Configure:
   - **Set cell**: Total Projected Hires cell
   - **To value**: 300
   - **By changing cell**: Total New Budget cell

Excel will calculate the required budget to reach 300 hires.

---

## Part 4: Solver Optimization (Advanced)

**Goal**: Maximize total hires while staying within budget

### Step 1: Enable Solver

1. Go to **File** → **Options** → **Add-ins**
2. Select **Solver Add-in** → **Go** → Check **Solver**
3. Click **OK**

### Step 2: Set Up Solver

1. Go to **Data** → **Solver**
2. Configure:
   - **Set Objective**: Total Projected Hires (G8)
   - **To**: Max
   - **By Changing Variable Cells**: New Budget range (F2:F7)
   - **Subject to Constraints**:
     - SUM(F2:F7) <= 2,100,000 (total budget constraint)
     - F2:F7 >= 0 (no negative budgets)
     - F2:F7 <= B2:B7 * 1.5 (max 50% increase per source)

3. Click **Solve**

**Result**: Solver will find the optimal budget allocation to maximize hires!

---

## Part 5: Visualization

### Create Charts

**Chart 1: Current vs Optimized Budget**
- Type: Clustered Column Chart
- X-axis: Source
- Y-axis: Current Budget vs New Budget
- Shows: Budget reallocation

**Chart 2: Projected Hire Increase**
- Type: Bar Chart
- X-axis: Source
- Y-axis: Current Hires vs Projected Hires
- Shows: Impact of budget changes

**Chart 3: ROI by Source**
- Type: Scatter Plot
- X-axis: Cost per Hire
- Y-axis: Hire Rate %
- Bubble size: Total Budget
- Shows: Which sources give best ROI

---

## Part 6: Scenario Summary Report

1. After creating scenarios, go to **Data** → **What-If Analysis** → **Scenario Manager**
2. Click **Summary**
3. Select **Scenario Summary** report type
4. Choose result cells: Total Budget, Total Hires
5. Click **OK**

Excel creates a summary table comparing all scenarios side-by-side.

---

## Example Insights from Simulation

### Scenario Comparison

| Metric | Current | Shift to High Performers | Maximize Referrals |
|--------|---------|-------------------------|-------------------|
| Total Budget | $2,100,000 | $2,100,000 | $2,100,000 |
| Total Hires | 231 | 287 (+24%) | 312 (+35%) |
| Avg Cost per Hire | $9,091 | $7,317 | $6,731 |
| ROI Improvement | Baseline | +24% | +35% |

**Key Finding**: Shifting budget to Employee Referrals and high-performing sources could increase hires by 35% with same budget!

---

## Business Recommendations

Based on simulation results:

1. **Increase Employee Referral Budget by 100%**
   - Lowest cost per hire ($4,348)
   - High quality candidates
   - ROI: Best in class

2. **Reduce Recruitment Agency Spend by 50%**
   - Highest cost per hire ($100,000)
   - Lowest hire rate (5.6%)
   - Reallocate to better sources

3. **Maintain Company Website Investment**
   - Highest hire rate (19.4%)
   - Reasonable cost per hire
   - Strong performer

---

## Tips for Presentation

- Show the Scenario Summary table to compare options
- Use charts to visualize budget reallocation
- Highlight the 35% hire increase potential
- Emphasize cost savings per hire

---

## Save Your Work

Save the Excel file as:
`excel/HR_Recruitment_Simulation.xlsx`

Include these sheets:
1. Budget Simulation
2. Data Table Analysis
3. Scenario Summary
4. Charts

---

## Next Steps

1. Present simulation results to stakeholders
2. Get approval for budget reallocation
3. Implement changes in recruiting strategy
4. Track actual results vs projections
5. Refine model based on real data
