from pydantic import BaseModel, Field
from typing import List
from langchain_core.messages import HumanMessage
from mas_orchestrator.utils.telemetry import record_node_timing
from dotenv import load_dotenv
load_dotenv()


from mas_orchestrator.state.schemas import MASState
from llm_clients.gemini_client import get_gemini_client
from llm_clients.prompts.correction_prompt import CORRECTION_SYSTEM_PROMPT
from shared.utils.db_utils import save_new_difficulties, save_correction_results

class GradedPhase(BaseModel):
    phase_name: str = Field(description="The name of the C2PCT phase (Phases 1-5).")
    score: int = Field(description="Score from 0 to 3 based on the rubric.", ge=0, le=3)
    justification: str = Field(description="Reason for the assigned score.")

class ReflectivePhase(BaseModel):
    phase_name: str = Field(description="The name of the C2PCT phase (Phases 6-7).")
    completed: bool = Field(description="True if the student genuinely engaged in reflection, False if missing or entirely off-topic.")
    extracted_feedback: str = Field(description="A concise summary of the student's stated difficulties, self-evaluation, or metacognition.")

class CorrectionOutput(BaseModel):
    academic_evaluations: List[GradedPhase] = Field(
        description="Exactly 5 evaluations for C2PCT Phases 1 through 5."
    )
    reflective_evaluations: List[ReflectivePhase] = Field(
        description="Exactly 2 evaluations for C2PCT Phases 6 and 7."
    )
    total_score: int = Field(description="The sum of all phase scores (maximum 15).")
    critical_errors: List[str] = Field(description="Direct, objective mistakes made in Phases 1-5.")

@record_node_timing("correction")
def run_correction_node(state: MASState) -> dict:
    """Evaluates the student's work strictly against the C2PCT rubric."""
    text_to_analyze = state.get("final_confirmed_text")
    diagnostic_data = state.get("diagnostic_data", {})
    subject = diagnostic_data.get("subject", "Unknown")
    session_id = state.get("session_id")
    langue = state.get("language", diagnostic_data.get("language", "en"))
    
    # Retrieves the solution manual/context from Qdrant
    retrieved_context = state.get("retrieved_context", "No reference material available.")    
    if not text_to_analyze:
        return {"error": "Correction Agent failed: No text to evaluate."}
        
    try:
        # Temperature is 0 for strict, objective grading
        llm = get_gemini_client(temperature=0.0) 
        structured_llm = llm.with_structured_output(CorrectionOutput)
        
        formatted_prompt = CORRECTION_SYSTEM_PROMPT.format(
            subject=subject,
            reference_materials="Official Course Materials", 
            retrieved_context=retrieved_context,
            student_text=text_to_analyze,
            langue=langue
        )
        response = structured_llm.invoke([HumanMessage(content=formatted_prompt)])
        correction_data = response.model_dump()
        if len(correction_data.get("academic_evaluations", [])) != 5:
            return {"error": "Correction Agent failed: Missing academic evaluations."}

        if session_id:
            self_reported_gaps = []
            for ref_phase in correction_data.get("reflective_evaluations", []):
                if ref_phase.get("completed") and ref_phase.get("extracted_feedback"):
                    formatted_gap = f"Self-Reported ({ref_phase['phase_name']}): {ref_phase['extracted_feedback']}"
                    self_reported_gaps.append(formatted_gap)
            
            if self_reported_gaps:
                save_new_difficulties(session_id, self_reported_gaps)            
            save_correction_results(session_id, correction_data)

        return {
            "correction_data": correction_data,
            "error": None
        }
        
    except Exception as e:
        return {"error": f"Correction Agent crashed: {str(e)}"}