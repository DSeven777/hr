from sqlalchemy import Column, Integer, String, Text, JSON, Float, ForeignKey
from sqlalchemy.orm import relationship
from src.infra.database import Base

class CandidateModel(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    years_of_experience = Column(Float, nullable=True) # Added field
    summary = Column(Text, nullable=True)
    skills = Column(JSON, nullable=True)
    education = Column(JSON, nullable=True)
    work_experience = Column(JSON, nullable=True)
    
    # Match context
    matched_job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    match_score = Column(Float, nullable=True)
    match_analysis = Column(Text, nullable=True) # Overall summary/recommendation
    match_details = Column(JSON, nullable=True) # Store full structured match result (scores per dimension, hard fail reasons)
    
    # Raw file
    resume_path = Column(String(512), nullable=True)
    
    job = relationship("JobModel")
