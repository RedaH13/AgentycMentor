from pydantic import BaseModel, Field
from typing import List
from langchain_core.messages import HumanMessage

from mas_orchestrator.state.schemas import MASState
from llm_clients.gemini_client import get_gemini_client
from llm_clients.prompts.guidance_prompts import GUIDANCE_SYSTEM_PROMPT

# structure for the Student Dashboard
class GuidanceOutput(BaseModel):
    subject_help: str = Field(description="Supplementary explanations and core concepts related to the detected subject.")
    methodology_coaching: str = Field(description="Step-by-step advice applying the Chaabi methodology C2PCT.")
    identified_difficulties: List[str] = Field(description="A list of specific difficulties or knowledge gaps detected in the student's work.")
    encouragement: str = Field(description="A short, encouraging closing sentence.")

def run_guidance_node(state: MASState) -> dict:
    """Generates pedagogical feedback and tracking metrics for the student."""
    text_to_analyze = state.get("final_confirmed_text")
    diagnostic_data = state.get("diagnostic_data", {})
    subject = diagnostic_data.get("subject", "General Academic Topic")
    
    if not text_to_analyze:
        return {"error": "Guidance Agent failed: No text found."}
        
    try:
        # Temperature is slightly higher (0.4) because we want pedagogical creativity
        llm = get_gemini_client(temperature=0.4) 
        structured_llm = llm.with_structured_output(GuidanceOutput)
        formatted_prompt = GUIDANCE_SYSTEM_PROMPT.format(
            subject=subject,
            student_text=text_to_analyze
        )
        
        response = structured_llm.invoke([HumanMessage(content=formatted_prompt)])        
        return {
            "guidance_data": response.model_dump(),
            "error": None
        }        
    except Exception as e:
        return {"error": f"Guidance Agent crashed: {str(e)}"}