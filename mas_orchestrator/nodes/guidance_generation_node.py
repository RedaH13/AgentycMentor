from pydantic import BaseModel, Field
from typing import List
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
load_dotenv()


from mas_orchestrator.state.schemas import MASState
from llm_clients.gemini_client import get_gemini_client
from llm_clients.prompts.guidance_prompts import GUIDANCE_SYSTEM_PROMPT
from shared.utils.db_utils import fetch_active_difficulties, save_new_difficulties, ensure_submission_exists

# structure for the Student Dashboard
class GuidanceOutput(BaseModel):
    subject_help: str = Field(description="Supplementary explanations and core concepts related to the detected subject.")
    methodology_coaching: str = Field(description="Step-by-step advice applying the Chaabi methodology C2PCT.")
    identified_difficulties: List[str] = Field(description="A list of specific difficulties or knowledge gaps detected in the student's work.")
    encouragement: str = Field(description="A short, encouraging closing sentence.")

def run_guidance_node(state: MASState) -> dict:
    """Generates pedagogical feedback and automates progress tracking."""
    
    text_to_analyze = state.get("final_confirmed_text")
    diagnostic_data = state.get("diagnostic_data", {})
    subject = diagnostic_data.get("subject", "Unknown")
    document_type = diagnostic_data.get("document_type", "Assignment")
    langue = diagnostic_data.get("langue","Unknown")

    student_id = state.get("student_id") # (passed in via API endpoint)
    session_id = state.get("session_id")

    retrieved_context = state.get("retrieved_context", "No course materials retrieved.")
    
    if not text_to_analyze or not student_id:
        return {"error": "Guidance Agent failed: Missing text or student ID."}
        
    try:
        #Fetch historical difficulties from SQL Server
        history_text = fetch_active_difficulties(student_id, subject) 
        llm = get_gemini_client(temperature=0.4) 
        structured_llm = llm.with_structured_output(GuidanceOutput)
        
        # Inject history and current text into guid_prompt
        formatted_prompt = GUIDANCE_SYSTEM_PROMPT.format(
            subject=subject,
            historical_difficulties=history_text,
            retrieved_context=retrieved_context,
            student_text=text_to_analyze,
            langue=diagnostic_data.get("langue","en")
        )
        
        response = structured_llm.invoke([HumanMessage(content=formatted_prompt)])
        guidance_data = response.model_dump()
        
        # Save new difficulties to sql server
        new_difficulties = guidance_data.get("identified_difficulties", [])
        if session_id:
            ensure_submission_exists(
                session_id=session_id, student_id=student_id,
                subject=subject, document_type=document_type, 
                submission_text=text_to_analyze, 
                langue=langue)
            save_new_difficulties(session_id, new_difficulties)      
        return {
            "guidance_data": guidance_data,
            "error": None
        }
        
    except Exception as e:
        return {"error": f"Guidance Agent crashed: {str(e)}"}