from pydantic import BaseModel, Field
from typing import Literal
from langchain_core.messages import HumanMessage
from mas_orchestrator.state.schemas import MASState
from llm_clients.gemini_client import get_gemini_client
from llm_clients.prompts.diagnostic_prompts import DIAGNOSTIC_SYSTEM_PROMPT
from dotenv import load_dotenv
load_dotenv()


# schema the agent MUST return
class DiagnosticOutput(BaseModel):
    subject: str = Field(description="The academic subject, e.g., Mathematics, Physics, Literature, Unknown")
    langue: str = Field(description="The primary language of the text, e.g., English, French, Spanish")
    is_readable: bool = Field(description="True if the text is coherent enough to be evaluated")
    structural_issues: str = Field(description="Brief description of missing parts or severe formatting errors, or 'None'")
    
    document_type: Literal["Homework", "Exam", "Essay", "Lab Report", "Unknown"] = Field(
        description="The category of the academic submission"
    )
    answer_format: Literal["Free-text", "Multiple-choice", "Equations", "Mixed", "Unknown"] = Field(
        description="The dominant format of the answers provided by the student"
    )
    completion_status: Literal["Complete", "Partial", "Cut-off", "Empty"] = Field(
        description="Indicates if the document appears to be a full assignment or is missing parts"
    )
    requires_math_engine: bool = Field(
        description="True if the document contains equations or formulas needing specialized evaluation"
    )

def run_diagnostic_node(state: MASState) -> dict:
    """Analyzes the confirmed text to determine document structure and routing metadata"""
    text_to_analyze = state.get("final_confirmed_text")
    if not text_to_analyze:
        return {"error": "Diagnostic Agent failed: No confirmed text found in state."}
        
    try:
        # Initialize Gemini with very low temperature for deterministic classification
        llm = get_gemini_client(temperature=0.0) 
        
        # Bind the Pydantic schema directly to the Gemini client
        structured_llm = llm.with_structured_output(DiagnosticOutput)
        formatted_prompt = DIAGNOSTIC_SYSTEM_PROMPT.format(ocr_text=text_to_analyze)
        
        # Invoke the model. It automatically returns a validated Pydantic object
        response = structured_llm.invoke([HumanMessage(content=formatted_prompt)])
        diagnostic_data = response.model_dump()
        state["langue"] = diagnostic_data["langue"]
        return {
            # Convert the Pydantic object back to a standard dictionary for the state
            "diagnostic_data": response.model_dump(),
            "error": None
        }
        
    except Exception as e:
        return {"error": f"Diagnostic Agent crashed: {str(e)}"}