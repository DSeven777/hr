from sqlalchemy import Column, Integer, String, Text, JSON
from src.infra.database import Base

class JobModel(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    department = Column(String(255), nullable=True)
    required_skills = Column(JSON, nullable=True)  # List of strings
    nice_to_have_skills = Column(JSON, nullable=True) # List of strings
    required_experience_years = Column(Integer, default=0)
    degree_requirement = Column(String(255), nullable=True)
    responsibilities = Column(Text, nullable=True)
    raw_text = Column(Text, nullable=True)
