"""
Job Description Generator Module

Leverages Gemini's generative capabilities to create comprehensive, tailored
job descriptions with industry-specific terminology and structural consistency.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union

from pydantic import BaseModel, Field

from src.modules.gemini.client import GeminiService
from src.utils.error_handling import handle_api_error

logger = logging.getLogger(__name__)

class JobDescriptionRequest(BaseModel):
    """Structured request for job description generation."""
    title: str = Field(..., description="Job title")
    department: str = Field(..., description="Department name")
    seniority: str = Field(..., description="Seniority level")
    employment_type: str = Field(default="Full-time", description="Type of employment")
    location: Optional[str] = Field(default=None, description="Job location")
    salary_range: Optional[str] = Field(default=None, description="Salary range")
    company_description: Optional[str] = Field(default=None, description="Custom company description")
    custom_requirements: Optional[List[str]] = Field(default=None, description="Specific job requirements")
    tone: str = Field(default="professional", description="Tone of the job description")

class JobDescriptionResponse(BaseModel):
    """Structured response from job description generation."""
    title: str = Field(..., description="Full job title")
    overview: str = Field(..., description="Paragraph about the role")
    key_responsibilities: List[str] = Field(..., description="List of key responsibilities")
    required_qualifications: List[str] = Field(..., description="List of required qualifications")
    preferred_qualifications: List[str] = Field(..., description="List of preferred qualifications")
    benefits: List[str] = Field(..., description="List of benefits and perks")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Generation metadata")

class JobDescriptionGenerator:
    """
    Advanced job description generator with dynamic templating and contextual awareness.
    
    This service leverages Gemini's generative capabilities to create comprehensive,
    tailored job descriptions with industry-specific terminology, structural consistency,
    and parameter-driven customization.
    """
    
    _instance = None
    
    def __new__(cls):
        """Implement singleton pattern for efficient resource usage."""
        if cls._instance is None:
            cls._instance = super(JobDescriptionGenerator, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the generator with knowledge bases and caching."""
        if self._initialized:
            return
            
        self.template_cache = {}
        self.industry_knowledge_base = self._initialize_knowledge_base()
        self._initialized = True
        logger.info("Job Description Generator initialized")
    
    def _initialize_knowledge_base(self) -> Dict[str, Dict[str, Any]]:
        """Initialize industry-specific terminology and requirements database."""
        # In production, this would load from a database or knowledge graph
        return {
            "engineering": {
                "skills": ["software development", "system design", "algorithms", "data structures"],
                "certifications": ["AWS", "Azure", "Google Cloud", "Kubernetes"],
                "frameworks": ["React", "Angular", "Vue", "Django", "Flask", "Spring"]
            },
            "design": {
                "skills": ["user research", "wireframing", "prototyping", "usability testing"],
                "tools": ["Figma", "Sketch", "Adobe XD", "InVision"],
                "methodologies": ["Design Thinking", "Agile UX", "Lean UX"]
            },
            "marketing": {
                "skills": ["campaign management", "market research", "content strategy", "analytics"],
                "platforms": ["Google Analytics", "HubSpot", "Salesforce", "Marketo"],
                "certifications": ["Google Ads", "HubSpot Marketing", "Facebook Blueprint"]
            },
            "customer_support": {
                "skills": ["problem solving", "communication", "product knowledge", "empathy"],
                "tools": ["Zendesk", "Intercom", "Freshdesk", "Salesforce Service Cloud"],
                "certifications": ["ITIL", "HDI", "Customer Service Professional"]
            }
        }
    
    def _get_industry_context(self, department: str) -> Dict[str, Any]:
        """Retrieve industry-specific context for the given department."""
        normalized_dept = department.lower().replace(" ", "_")
        
        # Find the closest matching department or fallback to generic
        for key in self.industry_knowledge_base:
            if key in normalized_dept or normalized_dept in key:
                return self.industry_knowledge_base[key]
        
        # Return generic context if no match found
        return {"skills": [], "tools": [], "methodologies": [], "certifications": []}
    
    @handle_api_error(default_return_factory=lambda: {"error": "Failed to generate job description"})
    async def generate_job_description(self, request: JobDescriptionRequest) -> JobDescriptionResponse:
        """
        Generate a comprehensive job description with dynamic industry context.
        
        Args:
            request: Structured job description generation request
            
        Returns:
            Complete job description with structured sections
        """
        # Get industry-specific context
        industry_context = self._get_industry_context(request.department)
        
        # Experience requirements mapping based on seniority
        experience_map = {
            "intern": "0-1 years",
            "junior": "1-3 years",
            "mid-level": "3-5 years",
            "senior": "5-8 years",
            "lead": "8+ years",
            "principal": "10+ years",
            "director": "12+ years"
        }
        
        # Normalize seniority and get experience requirement
        normalized_seniority = request.seniority.lower().replace("-", "").replace(" ", "")
        experience_requirement = next((exp for key, exp in experience_map.items() 
                                     if key in normalized_seniority), "3-5 years")
        
        # Build comprehensive prompt with all contextual elements
        prompt = f"""
        Generate a detailed, compelling job description for a {request.seniority} {request.title} position in the {request.department} department.

        COMPANY CONTEXT:
        {request.company_description or "A forward-thinking company leveraging technology to drive innovation and growth."}
        
        POSITION DETAILS:
        - Title: {request.seniority} {request.title}
        - Department: {request.department}
        - Employment Type: {request.employment_type}
        - Location: {request.location or "Flexible"}
        - Experience Required: {experience_requirement}
        - Salary Range: {request.salary_range or "Competitive, based on experience"}
        
        INDUSTRY-SPECIFIC CONTEXT:
        - Relevant Skills: {', '.join(industry_context.get('skills', []))}
        - Tools/Platforms: {', '.join(industry_context.get('tools', []) + industry_context.get('platforms', []))}
        - Methodologies: {', '.join(industry_context.get('methodologies', []))}
        - Relevant Certifications: {', '.join(industry_context.get('certifications', []))}
        
        CUSTOM REQUIREMENTS:
        {request.custom_requirements and '- ' + '\\n- '.join(request.custom_requirements) or 'Generate appropriate requirements based on the role.'}
        
        TONE GUIDANCE:
        Use a {request.tone} tone that reflects the company culture and appeals to qualified candidates.
        
        FORMAT THE JOB DESCRIPTION WITH THESE SECTIONS:
        1. About the Role (compelling overview)
        2. Key Responsibilities (7-10 bullet points)
        3. Required Qualifications (5-7 bullet points)
        4. Preferred Qualifications (3-5 bullet points)
        5. Benefits & Perks (5 bullet points)
        
        Return the response in JSON format with these exact keys:
        {
            "title": "full job title",
            "overview": "paragraph about the role",
            "key_responsibilities": ["responsibility 1", "responsibility 2", ...],
            "required_qualifications": ["qualification 1", "qualification 2", ...],
            "preferred_qualifications": ["qualification 1", "qualification 2", ...],
            "benefits": ["benefit 1", "benefit 2", ...]
        }
        """
        
        # Generate content using Gemini with appropriate temperature
        # Higher temperature for more creative descriptions
        response_text = await GeminiService.generate_content(prompt, temperature=0.7, max_tokens=1500)
        
        # Parse the JSON response with fallback mechanisms
        job_description = GeminiService.parse_json_response(response_text)
        
        # Add metadata for downstream processing
        job_description["metadata"] = {
            "generated_timestamp": datetime.now().isoformat(),
            "parameters": {
                "title": request.title,
                "department": request.department,
                "seniority": request.seniority,
                "employment_type": request.employment_type,
                "location": request.location,
                "salary_range": request.salary_range
            }
        }
        
        # Create validated response object
        return JobDescriptionResponse(**job_description)