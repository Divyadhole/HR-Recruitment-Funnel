"""
FastAPI REST API for HR Recruitment Funnel Analytics
Run with: uvicorn api.main:app --reload
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import sqlite3
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(
    title="HR Recruitment Funnel API",
    description="REST API for accessing recruitment funnel metrics and ML predictions",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class FunnelMetrics(BaseModel):
    total_applicants: int
    hired_count: int
    hire_rate: float
    avg_time_to_hire: float

class StageMetrics(BaseModel):
    stage: str
    applicants: int
    pass_rate: float
    drop_off_rate: float

class SourceMetrics(BaseModel):
    source: str
    total_applicants: int
    hired: int
    hire_rate: float

# Database connection
def get_db_connection():
    """Get SQLite database connection"""
    conn = sqlite3.connect('recruitment.db')
    conn.row_factory = sqlite3.Row
    return conn

# Routes
@app.get("/")
def read_root():
    """API root endpoint"""
    return {
        "message": "HR Recruitment Funnel Analytics API",
        "version": "1.0.0",
        "endpoints": {
            "/metrics": "Overall funnel metrics",
            "/stages": "Stage-by-stage metrics",
            "/sources": "Source effectiveness metrics",
            "/docs": "Interactive API documentation"
        }
    }

@app.get("/metrics", response_model=FunnelMetrics)
def get_overall_metrics(
    source: Optional[str] = Query(None, description="Filter by recruiting source"),
    department: Optional[str] = Query(None, description="Filter by department")
):
    """Get overall recruitment funnel metrics"""
    
    conn = get_db_connection()
    
    query = """
        SELECT 
            COUNT(DISTINCT Applicant_ID) as total_applicants,
            SUM(CASE WHEN Status = 'Hired' THEN 1 ELSE 0 END) as hired_count,
            AVG(CASE WHEN Status = 'Hired' THEN Days_Since_Application END) as avg_time_to_hire
        FROM applicant_stages
        WHERE 1=1
    """
    
    params = []
    if source:
        query += " AND Source = ?"
        params.append(source)
    if department:
        query += " AND Department = ?"
        params.append(department)
    
    result = conn.execute(query, params).fetchone()
    conn.close()
    
    total = result['total_applicants']
    hired = result['hired_count']
    
    return FunnelMetrics(
        total_applicants=total,
        hired_count=hired,
        hire_rate=round((hired / total * 100) if total > 0 else 0, 2),
        avg_time_to_hire=round(result['avg_time_to_hire'] or 0, 1)
    )

@app.get("/stages", response_model=List[StageMetrics])
def get_stage_metrics():
    """Get metrics for each hiring stage"""
    
    conn = get_db_connection()
    
    query = """
        SELECT 
            Stage,
            COUNT(*) as applicants,
            SUM(CASE WHEN Status != 'Rejected' THEN 1 ELSE 0 END) as passed,
            SUM(CASE WHEN Status = 'Rejected' THEN 1 ELSE 0 END) as rejected
        FROM applicant_stages
        GROUP BY Stage
        ORDER BY Stage_Sequence
    """
    
    results = conn.execute(query).fetchall()
    conn.close()
    
    metrics = []
    for row in results:
        total = row['applicants']
        passed = row['passed']
        rejected = row['rejected']
        
        metrics.append(StageMetrics(
            stage=row['Stage'],
            applicants=total,
            pass_rate=round((passed / total * 100) if total > 0 else 0, 2),
            drop_off_rate=round((rejected / total * 100) if total > 0 else 0, 2)
        ))
    
    return metrics

@app.get("/sources", response_model=List[SourceMetrics])
def get_source_metrics():
    """Get effectiveness metrics for each recruiting source"""
    
    conn = get_db_connection()
    
    query = """
        SELECT 
            Source,
            COUNT(DISTINCT Applicant_ID) as total_applicants,
            SUM(CASE WHEN Status = 'Hired' THEN 1 ELSE 0 END) as hired
        FROM applicant_stages
        GROUP BY Source
        ORDER BY hired DESC
    """
    
    results = conn.execute(query).fetchall()
    conn.close()
    
    metrics = []
    for row in results:
        total = row['total_applicants']
        hired = row['hired']
        
        metrics.append(SourceMetrics(
            source=row['Source'],
            total_applicants=total,
            hired=hired,
            hire_rate=round((hired / total * 100) if total > 0 else 0, 2)
        ))
    
    return metrics

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
