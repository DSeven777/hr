from pydantic import BaseModel, Field
from typing import List, Optional

class JobDescription(BaseModel):
    model_config = {"populate_by_name": True}

    title: str = Field(description="Job title", alias="Job Title")
    department: Optional[str] = Field(None, description="Department name", alias="Department")
    required_skills: List[str] = Field(description="List of required skills", alias="Required Skills")
    nice_to_have_skills: List[str] = Field(default_factory=list, description="List of preferred skills", alias="Nice to have Skills")
    required_experience_years: Optional[int] = Field(0, description="Minimum years of experience required", alias="Required Experience Years")
    degree_requirement: Optional[str] = Field("Not Specified", description="Minimum degree required", alias="Degree Requirement")
    responsibilities: str = Field(description="Detailed job responsibilities", alias="Responsibilities")
    raw_text: Optional[str] = Field(None, description="Raw text of the JD", exclude=True)
