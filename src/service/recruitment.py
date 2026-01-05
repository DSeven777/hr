from sqlalchemy.orm import Session
from src.chain.resume_chain import ResumeParseChain
from src.chain.job_chain import JobAnalysisChain
from src.chain.match_chain import MatchChain
from src.domain.resume import Resume
from src.domain.job import JobDescription
from src.domain.match import MatchResult
from src.models.candidate import CandidateModel
from src.models.job import JobModel
from src.utils.pdf import extract_text_from_pdf

class RecruitmentService:
    """Service layer for recruitment operations."""
    
    def __init__(self):
        # Initialize chains lazily or eagerly
        self.resume_chain = ResumeParseChain()
        self.job_chain = JobAnalysisChain()
        self.match_chain = MatchChain()
    
    def parse_resume(self, text: str) -> Resume:
        """Parse a resume text."""
        return self.resume_chain.parse(text)
    
    def parse_job(self, text: str) -> JobDescription:
        """Parse a JD text."""
        return self.job_chain.analyze(text)
    
    def match(self, resume: Resume, job: JobDescription) -> MatchResult:
        """Match a candidate against a job."""
        return self.match_chain.evaluate(job, resume)

    def process_pdf_application(self, db: Session, file_content: bytes, job_id: int) -> dict:
        """
        Process a PDF application:
        1. Parse PDF to text
        2. Extract Resume structure
        3. Fetch Job from DB
        4. Match Resume vs Job
        5. Save Candidate + Match Result to DB
        """
        # 1. Extract text
        text = extract_text_from_pdf(file_content)
        if not text or len(text.strip()) < 10:
             raise ValueError("Could not extract sufficient text from PDF. Ensure it is a text-based PDF, not a scanned image.")

        # 3. Fetch Job (Do this early to fail fast)
        # Note: If processing batch, caller should optimize fetching job once.
        # But for simplicity here we fetch inside or let caller pass job_domain if we refactor.
        # For now, let's keep it simple.
        job_record = db.query(JobModel).filter(JobModel.id == job_id).first()
        if not job_record:
            raise ValueError(f"Job with ID {job_id} not found")
            
        # Convert JobModel to JobDescription domain object
        job_domain = JobDescription(
            **{
                "Job Title": job_record.title,
                "Department": job_record.department,
                "Required Skills": job_record.required_skills or [],
                "Nice to have Skills": job_record.nice_to_have_skills or [],
                "Required Experience Years": job_record.required_experience_years,
                "Degree Requirement": job_record.degree_requirement or "Not Specified",
                "Responsibilities": job_record.responsibilities or ""
            }
        )

        # 2. Parse Resume (This is the slow LLM call #1)
        # TODO: Optimize by running parallel with something if possible, but here we need resume to match.
        try:
            resume = self.parse_resume(text)
        except Exception as e:
            # If resume parsing fails (e.g. strict validation), we should NOT proceed to match.
            # We should raise exception so that no partial data is saved.
            # The user reported empty data in DB, which means match() was called with empty/failed resume?
            # Or parse_resume returned a partial object?
            # LangChain's structured_output might raise validation error.
            # We re-raise to stop execution.
            raise ValueError(f"Resume parsing failed: {str(e)}")
        
        # 4. Match (This is the slow LLM call #2)
        match_result = self.match(resume, job_domain)
        
        # 5. Save to DB
        candidate = CandidateModel(
            name=resume.name,
            email=resume.email,
            phone=resume.phone,
            summary=resume.summary,
            skills=resume.skills,
            education=[e.model_dump(by_alias=True) for e in resume.education],
            work_experience=[w.model_dump(by_alias=True) for w in resume.work_experience],
            # Store years_of_experience in summary or new field if model update allowed, 
            # for now let's append to summary if summary is string
            # summary = (resume.summary or "") + f"\nYears of Exp: {resume.years_of_experience}"
            matched_job_id=job_id,
            match_score=match_result.overall_score,
            match_analysis=match_result.summary + "\nRecommendation: " + match_result.recommendation
        )
        
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        
        return {
            "candidate_id": candidate.id,
            "resume": resume,
            "match_result": match_result
        }

    async def process_batch_applications(self, db: Session, files: list[tuple[str, bytes]], job_id: int):
        """
        Process multiple PDF applications concurrently for the same job.
        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        # 1. Fetch Job Once
        job_record = db.query(JobModel).filter(JobModel.id == job_id).first()
        if not job_record:
            raise ValueError(f"Job with ID {job_id} not found")
        
        # Prepare Job Domain Object (Thread-safe read-only)
        job_domain = JobDescription(
            **{
                "Job Title": job_record.title,
                "Department": job_record.department,
                "Required Skills": job_record.required_skills or [],
                "Nice to have Skills": job_record.nice_to_have_skills or [],
                "Required Experience Years": job_record.required_experience_years,
                "Degree Requirement": job_record.degree_requirement or "Not Specified",
                "Responsibilities": job_record.responsibilities or ""
            }
        )
        
        # 2. Define worker function for parallel execution
        # Note: We CANNOT pass the `db` session to threads. 
        # We must return the data, and write to DB in the main thread.
        def process_single_file_llm_only(filename: str, content: bytes) -> dict:
            try:
                # 1. Extract text
                text = extract_text_from_pdf(content)
                if not text or len(text.strip()) < 10:
                    return {"filename": filename, "status": "error", "error": "Empty or invalid PDF text"}

                # 2. Parse Resume
                resume = self.parse_resume(text)
                
                # 3. Match
                match_result = self.match(resume, job_domain)
                
                return {
                    "filename": filename,
                    "status": "success",
                    "resume": resume,
                    "match_result": match_result
                }
            except Exception as e:
                return {"filename": filename, "status": "error", "error": str(e)}

        # 3. Run LLM tasks in parallel
        # Adjust max_workers based on your API rate limits (e.g., 3-5 for OpenAI)
        loop = asyncio.get_event_loop()
        tasks = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            for filename, content in files:
                tasks.append(
                    loop.run_in_executor(executor, process_single_file_llm_only, filename, content)
                )
            
            # Wait for all tasks to complete
            processed_results = await asyncio.gather(*tasks)

        # 4. Save to DB sequentially (Main Thread)
        final_output = []
        for res in processed_results:
            if res["status"] == "success":
                resume = res["resume"]
                match_result = res["match_result"]
                
                candidate = CandidateModel(
                    name=resume.name,
                    email=resume.email,
                    phone=resume.phone,
                    summary=resume.summary,
                    # years_of_experience is not in DB model yet, skip or add column. 
                    # Assuming user didn't ask for DB schema change yet, but we extracted it.
                    # Let's just use it for Matching logic for now.
                    skills=resume.skills,
                    education=[e.model_dump(by_alias=True) for e in resume.education],
                    work_experience=[w.model_dump(by_alias=True) for w in resume.work_experience],
                    matched_job_id=job_id,
                    match_score=match_result.overall_score,
                    match_analysis=match_result.summary + "\nRecommendation: " + match_result.recommendation
                )
                db.add(candidate)
                # Commit each one or batch commit
                try:
                    db.commit()
                    db.refresh(candidate)
                    res["data"] = {
                        "candidate_id": candidate.id,
                        "resume": resume,
                        "match_result": match_result
                    }
                    # Clean up temp objects to avoid serialization issues if any
                    del res["resume"] 
                    del res["match_result"]
                except Exception as e:
                    res["status"] = "error"
                    res["error"] = f"DB Save Error: {str(e)}"
            
            final_output.append(res)
                
        return final_output
