from pathlib import Path
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from src.infra.llm import OpenAIProvider
from src.domain.job import JobDescription

class JobAnalysisChain:
    """Chain for analyzing JD text into structured JobDescription object."""
    
    def __init__(self):
        self.llm = OpenAIProvider().get_model()
        self.parser = PydanticOutputParser(pydantic_object=JobDescription)
        
        template_path = Path(__file__).parents[1] / "prompt" / "job_analysis.jinja2"
        template_content = template_path.read_text(encoding="utf-8")
        
        # Inject format instructions into the prompt
        self.prompt = PromptTemplate(
            template=template_content + "\n\n{{format_instructions}}",
            input_variables=["jd_text"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
            template_format="jinja2"
        )
        
    def analyze(self, jd_text: str) -> JobDescription:
        """Analyze JD text."""
        try:
            chain = self.prompt | self.llm | self.parser
            res = chain.invoke({"jd_text": jd_text})
            return res
        except Exception as e:
            # Fallback or re-raise
            raise ValueError(f"Failed to parse job description: {e}")
