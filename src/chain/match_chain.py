from pathlib import Path
from langchain_core.prompts import PromptTemplate
from src.infra.llm import OpenAIProvider
from src.domain.match import MatchResult
from src.domain.resume import Resume
from src.domain.job import JobDescription

class MatchChain:
    """Chain for evaluating candidate fit against a job description."""
    
    def __init__(self):
        self.llm = OpenAIProvider().get_model()
        template_path = Path(__file__).parents[1] / "prompt" / "match_evaluate.jinja2"
        
        template_content = template_path.read_text(encoding="utf-8")
        
        self.prompt = PromptTemplate(
            template=template_content,
            input_variables=["job", "resume"],
            template_format="jinja2"
        )
        
    def evaluate(self, job: JobDescription, resume: Resume) -> MatchResult:
        """Evaluate match."""
        structured_llm = self.llm.with_structured_output(MatchResult, method="json_mode")
        chain = self.prompt | structured_llm
        # Pass objects directly; Jinja2 template will access attributes (e.g. job.title)
        return chain.invoke({"job": job, "resume": resume})
