from pathlib import Path
from langchain_core.prompts import PromptTemplate
from src.infra.llm import OpenAIProvider
from src.domain.resume import Resume

class ResumeParseChain:
    """Chain for parsing raw resume text into structured Resume object."""
    
    def __init__(self):
        self.llm = OpenAIProvider().get_model()
        template_path = Path(__file__).parents[1] / "prompt" / "resume_parse.jinja2"
        
        # Load template from file manually to avoid PromptTemplate.from_file issues with jinja2/input_variables
        template_content = template_path.read_text(encoding="utf-8")
        
        self.prompt = PromptTemplate(
            template=template_content,
            input_variables=["resume_text"],
            template_format="jinja2"
        )
        
    def parse(self, resume_text: str) -> Resume:
        """Parse resume text."""
        # Force JSON mode explicitly for models that might not support function calling robustly
        # or when structured_output fails to produce valid JSON directly.
        # However, with_structured_output is the standard way. 
        # The error suggests the model returned text like "Here is the extracted..." instead of JSON.
        
        # We can try to enforce strict JSON output or switch to a Pydantic parser if the model is chatty.
        structured_llm = self.llm.with_structured_output(Resume, method="json_mode")
        chain = self.prompt | structured_llm
        return chain.invoke({"resume_text": resume_text})
