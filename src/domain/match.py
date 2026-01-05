from pydantic import BaseModel, Field

class MatchDimension(BaseModel):
    model_config = {"populate_by_name": True}

    dimension: str = Field(description="Dimension name (e.g., Skills, Experience)", alias="Dimension")
    score: float = Field(..., ge=0, le=100, description="Score for this dimension (0-100)", alias="Score")
    analysis: str = Field(description="Detailed analysis/reasoning for the score", alias="Analysis")

class MatchResult(BaseModel):
    model_config = {"populate_by_name": True}
    
    candidate_name: str = Field(..., alias="Candidate Name")
    job_title: str = Field(..., alias="Job Title")
    overall_score: float = Field(..., ge=0, le=100, description="Overall match score", alias="Overall Score")
    skill_match: MatchDimension = Field(..., alias="Skills Match")
    experience_match: MatchDimension = Field(..., alias="Experience Match")
    education_match: MatchDimension = Field(..., alias="Education Match")
    summary: str = Field(description="Executive summary of the match", alias="Summary")
    recommendation: str = Field(description="Hiring recommendation (Strong Hire, Hire, Weak Hire, No Hire)", alias="Recommendation")
