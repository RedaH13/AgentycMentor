from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage
from api.schemas.chat_schemas import ChatRequest
from mas_orchestrator.graphs.chat_graph import chat_router

router = APIRouter(prefix="/chat", tags=["Conversational Tutor"])

@router.post("/invoke")
async def invoke_chat_tutor(request: ChatRequest):
    """
    Standard REST endpoint to test the conversational agent.
    Maintains memory across requests using thread_id
    """
    try:
        # Config memory tracking for specific convers thread
        config = {"configurable": {"thread_id": request.thread_id}}
        
        # state payload
        input_state = {
            "messages": [HumanMessage(content=request.message)],
            "student_id": request.student_id,
            "student_report": request.student_report
        }
        
        # exec cyclic graph
        result = chat_router.invoke(input_state, config=config)
        
        # final Socratic response generated
        final_ai_message = result["messages"][-1].content
        
        return {
            "thread_id": request.thread_id,
            "response": final_ai_message
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'orchestration: {str(e)}")