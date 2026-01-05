from pathlib import Path
from langchain_core.prompts import PromptTemplate
from src.infra.llm import OpenAIProvider
from src.domain.resume import Resume

class ResumeParseChain:
    """Chain for parsing raw resume text into structured Resume object."""
    
    def __init__(self):
        self.llm = OpenAIProvider().get_model()
        template_path = Path(__file__).parents[1] / "prompt" / "resume_parse.jinja2"
        
        template_content = template_path.read_text(encoding="utf-8")
        
        self.prompt = PromptTemplate(
            template=template_content,
            input_variables=["resume_text"],
            template_format="jinja2"
        )
        
    def parse(self, resume_text: str) -> Resume:
        """Parse resume text."""
        structured_llm = self.llm.with_structured_output(Resume, method="json_mode")
        chain = self.prompt | structured_llm
        return chain.invoke({"resume_text": resume_text})
