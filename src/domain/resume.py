from pydantic import BaseModel, Field
from typing import List, Optional

class Education(BaseModel):
    model_config = {"populate_by_name": True}

    school: Optional[str] = Field(None, description="Name of the school/university", alias="School")
    degree: Optional[str] = Field(None, description="Degree obtained (e.g., BS, MS, PhD)", alias="Degree")
    major: Optional[str] = Field(None, description="Major field of study", alias="Major")
    dates: Optional[str] = Field(None, description="Time period", alias="Dates")
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class WorkExperience(BaseModel):
    model_config = {"populate_by_name": True}
    
    company: Optional[str] = Field(None, description="Company name", alias="Company")
    role: Optional[str] = Field(None, description="Job title", alias="Role")
    dates: Optional[str] = Field(None, description="Time period", alias="Dates")
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = Field(None, description="Details of responsibilities and achievements", alias="Description")

class Resume(BaseModel):
    model_config = {"populate_by_name": True}

    name: Optional[str] = Field(None, description="Candidate's full name", alias="Name")
    email: Optional[str] = Field(None, description="Email address", alias="Email")
    phone: Optional[str] = Field(None, description="Phone number", alias="Phone")
    years_of_experience: float = Field(0.0, description="Total years of professional work experience (excluding internships if possible, or labeled)", alias="Years of Experience")
    summary: Optional[str] = Field(None, description="Professional summary", alias="Summary")
    skills: List[str] = Field(default_factory=list, description="List of technical and soft skills", alias="Skills")
    education: List[Education] = Field(default_factory=list, alias="Education")
    work_experience: List[WorkExperience] = Field(default_factory=list, alias="Work Experience")
    raw_text: Optional[str] = Field(None, description="Raw text content of the resume", exclude=True)
