from pydantic import BaseModel, Field
from typing import List
from langchain_core.messages import HumanMessage

from mas_orchestrator.state.schemas import MASState
from llm_clients.gemini_client import get_gemini_client
from llm_clients.prompts.feedback_prompts import FEEDBACK_SYSTEM_PROMPT
from shared.utils.db_utils import save_feedback_report

class FeedbackOutput(BaseModel):
    professor_summary: str = Field(
        description="A 2-sentence plain text summary of the student's performance, justifying the final grade for the professor to review."
    )
    pedagogical_warning: str = Field(
        description="A brief warning about specific conceptual blockers, critical calculation errors, or severe methodology failures. Keep it concise."
    )
    student_draft_report: str = Field(
        description="An empathetic, constructive feedback report addressed to the student, focusing on actionable steps. Do not include raw numerical grades."
    )

def run_feedback_node(state: MASState) -> dict:
    """Synthesizes technical grades and guidance into a student-friendly report."""
    
    guidance = state.get("guidance_data", {})
    correction = state.get("correction_data", {})
    subject = state.get("diagnostic_data", {}).get("subject", "Unknown Subject")
    langue = state.get("language", state.get("diagnostic_data", {}).get("language", "en"))
    retrieved_context = state.get("retrieved_context", "No course materials provided.")

    if not guidance or not correction:
        return {"error": "Feedback Agent failed: Missing guidance or correction data."}
        
    try:
        llm = get_gemini_client(temperature=0.4) 
        structured_llm = llm.with_structured_output(FeedbackOutput)
        
        formatted_prompt = FEEDBACK_SYSTEM_PROMPT.format(
            subject= subject,
            guidance_data=guidance,
            correction_data=correction,
            langue=langue,
            retrieved_context=retrieved_context
        )        
        response = structured_llm.invoke([HumanMessage(content=formatted_prompt)])
        feedback_data = response.model_dump()

        if state.get("session_id"):
            save_feedback_report(state["session_id"], feedback_data)
        return {
            "feedback_data": feedback_data,
            "error": None
        }        
    except Exception as e:
        return {"error": f"Feedback Agent crashed: {str(e)}"}