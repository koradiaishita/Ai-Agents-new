from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional

# Import core functionality
from modules.recruitment.job_description_generator import JobDescriptionGenerator

# Define API router
router = APIRouter()

# Data models
class JobDescriptionRequest(BaseModel):
    title: str
    department: str
    seniority: str
    employment_type: Optional[str] = "Full-time"
    location: Optional[str] = None
    salary_range: Optional[str] = None

# Endpoints
@router.post("/generate-job-description")
async def generate_job_description(request: JobDescriptionRequest):
    """Generate a job description based on parameters"""
    try:
        generator = JobDescriptionGenerator()
        result = await generator.generate_job_description(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """System health check endpoint"""
    return {"status": "healthy"}