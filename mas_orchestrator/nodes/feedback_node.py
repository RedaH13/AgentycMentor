from pydantic import BaseModel, Field
from typing import List
from langchain_core.messages import HumanMessage

from mas_orchestrator.state.schemas import MASState
from llm_clients.gemini_client import get_gemini_client
from llm_clients.prompts.feedback_prompts import FEEDBACK_SYSTEM_PROMPT

class FeedbackOutput(BaseModel):
    professor_summary: str = Field(
        description="A 2-sentence plain text summary of the student's performance, justifying the final grade for the professor to review."
    )
    # For the Student (Approved via Power BI later)
    student_strengths: str = Field(
        description="A short, plain-text paragraph highlighting what the student did well based on the rubric."
    )
    actionable_advice: str = Field(
        description="A plain-text paragraph providing specific steps for improvement based on the critical errors."
    )
    encouraging_closing: str = Field(
        description="A single encouraging sentence to close the feedback."
    )
    report_summary: str = Field(
        description="A cohesive, 3-4 sentence plain-text summary of the student's performance, blending their strengths with their core areas for improvement."
    )

def run_feedback_node(state: MASState) -> dict:
    """Synthesizes technical grades and guidance into a student-friendly report."""
    
    guidance = state.get("guidance_data", {})
    correction = state.get("correction_data", {})
    
    if not guidance or not correction:
        return {"error": "Feedback Agent failed: Missing guidance or correction data."}
        
    try:
        llm = get_gemini_client(temperature=0.4) 
        structured_llm = llm.with_structured_output(FeedbackOutput)
        
        formatted_prompt = FEEDBACK_SYSTEM_PROMPT.format(
            guidance_data=guidance,
            correction_data=correction
        )        
        response = structured_llm.invoke([HumanMessage(content=formatted_prompt)])
        return {
            "feedback_data": response.model_dump(),
            "error": None
        }        
    except Exception as e:
        return {"error": f"Feedback Agent crashed: {str(e)}"}