from pathlib import Path
from langchain_core.prompts import PromptTemplate
from src.infra.llm import OpenAIProvider
from src.domain.job import JobDescription

class JobAnalysisChain:
    """Chain for analyzing JD text into structured JobDescription object."""
    
    def __init__(self):
        self.llm = OpenAIProvider().get_model()
        template_path = Path(__file__).parents[1] / "prompt" / "job_analysis.jinja2"
        
        template_content = template_path.read_text(encoding="utf-8")
        
        self.prompt = PromptTemplate(
            template=template_content,
            input_variables=["jd_text"],
            template_format="jinja2"
        )
        
    def analyze(self, jd_text: str) -> JobDescription:
        """Analyze JD text."""
        structured_llm = self.llm.with_structured_output(JobDescription, method="json_mode")
        chain = self.prompt | structured_llm
        return chain.invoke({"jd_text": jd_text})
