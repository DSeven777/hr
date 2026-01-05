import sys
from typing import List
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import BaseModel, model_validator
from contextlib import asynccontextmanager
from pathlib import Path
from sqlalchemy.orm import Session
from loguru import logger
from src.service.recruitment import RecruitmentService
from src.domain.resume import Resume
from src.domain.job import JobDescription
from src.domain.match import MatchResult
from src.config import Config
from src.infra.database import get_db, init_db
from src.models.job import JobModel

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Validate configuration on startup
    try:
        Config.validate()
        # Initialize DB tables
        init_db()
    except ValueError as e:
        raise RuntimeError(f"Configuration Error: {e}")
    yield

# Configure logger
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("logs/app.log", rotation="500 MB", level="DEBUG")

app = FastAPI(
    title="Intelligent Recruitment System API",
    version="1.0.0",
    description="AI-powered Resume Parsing and Job Matching API",
    lifespan=lifespan,
    docs_url=None,  # Disable default docs
    redoc_url=None  # Disable default redoc
)

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

if not STATIC_DIR.exists():
    STATIC_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )

# Initialize service lazily
try:
    Config.validate()
    service = RecruitmentService()
except Exception as e:
    print(f"Warning: Failed to initialize service: {e}")
    service = None

class TextRequest(BaseModel):
    text: str

    @model_validator(mode='before')
    @classmethod
    def validate_text(cls, values):
        return values

class MatchRequest(BaseModel):
    resume: Resume
    job: JobDescription

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/v1/resume/parse/text", response_model=Resume, summary="Parse Resume Raw Text")
async def parse_resume_raw(request: Request):
    """
    Parse resume from raw text body (Content-Type: text/plain).
    """
    try:
        body_bytes = await request.body()
        text = body_bytes.decode("utf-8")
        
        logger.info("Received raw resume parse request")
        if len(text.strip()) < 10:
             return Resume(name="Unknown", raw_text=text)

        result = service.parse_resume(text)
        return result
    except Exception as e:
        logger.error(f"Error parsing resume: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/job/parse/text", response_model=JobDescription, summary="Parse JD Raw Text")
async def parse_job_raw(request: Request):
    """
    Parse JD from raw text body (Content-Type: text/plain).
    """
    try:
        body_bytes = await request.body()
        text = body_bytes.decode("utf-8")
        
        logger.info("Received raw JD parse request")
        return service.parse_job(text)
    except Exception as e:
        logger.error(f"Error parsing JD: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/resume/parse", response_model=Resume, summary="Parse Resume Text (JSON)")
def parse_resume(req: TextRequest):
    """
    Parse unstructured resume text into structured JSON.
    """
    try:
        logger.info("Received resume parse request")
        logger.debug(f"Resume text length: {len(req.text)}")
        if len(req.text.strip()) < 10:
             logger.warning("Resume text too short, returning empty resume")
             return Resume(name="Unknown", raw_text=req.text)

        result = service.parse_resume(req.text)
        logger.info("Resume parsed successfully")
        return result
    except Exception as e:
        logger.error(f"Error parsing resume: {str(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/job/parse", response_model=JobDescription, summary="Parse JD Text (JSON)")
def parse_job(req: TextRequest):
    """
    Parse unstructured Job Description text into structured JSON.
    """
    try:
        logger.info("Received JD parse request")
        return service.parse_job(req.text)
    except Exception as e:
        logger.error(f"Error parsing JD: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/match", response_model=MatchResult, summary="Match Resume with JD")
def match_candidate(req: MatchRequest):
    """
    Evaluate a candidate against a job description.
    """
    try:
        logger.info("Received match request")
        return service.match(req.resume, req.job)
    except Exception as e:
        logger.error(f"Error matching candidate: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/jobs", summary="Create Job in DB")
def create_job(job: JobDescription, db: Session = Depends(get_db)):
    """Create a new job posting in the database."""
    try:
        db_job = JobModel(
            title=job.title,
            department=job.department,
            required_skills=job.required_skills,
            nice_to_have_skills=job.nice_to_have_skills,
            required_experience_years=job.required_experience_years,
            degree_requirement=job.degree_requirement,
            responsibilities=job.responsibilities
        )
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        return {"id": db_job.id, "message": "Job created successfully"}
    except Exception as e:
        logger.error(f"Error creating job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/application/submit", summary="Upload PDF Resume & Match")
async def submit_application(
    job_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a PDF resume, parse it, match against the specified Job ID, and save to DB.
    """
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
            
        content = await file.read()
        result = service.process_pdf_application(db, content, job_id)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Error processing application: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/application/batch-submit", summary="Batch Upload PDF Resumes & Match")
async def batch_submit_application(
    job_id: int = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Batch Upload multiple PDF resumes, parse them, match against the specified Job ID, and save to DB.
    """
    try:
        # Validate files
        valid_files = []
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                continue
            content = await file.read()
            valid_files.append((file.filename, content))
            
        if not valid_files:
             raise HTTPException(status_code=400, detail="No valid PDF files provided")

        result = await service.process_batch_applications(db, valid_files, job_id)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Error processing batch application: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
