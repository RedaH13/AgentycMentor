import requests
import os
import httpx
from mas_orchestrator.state.schemas import MASState
from mas_orchestrator.utils.telemetry import record_node_timing


@record_node_timing("ocr")
async def run_ocr_node(state: MASState) -> dict:
    """Delegates perception to the independent ocr_service without deadlocking FastAPI."""
    file_path = state.get("file_path")
    
    if not file_path or not os.path.exists(file_path):
        return {"error": "No valid file_path provided to OCR node"}

    try:
        async with httpx.AsyncClient() as client:
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f, "image/jpeg")}
                response = await client.post("http://127.0.0.1:8000/ocr/api/v1/ocr/extract", files=files, timeout=30.0)
                
        if response.status_code == 200:
            ocr_result = response.json()
        
            extracted = (
                ocr_result.get("full_text")
                or ocr_result.get("text")
                or ocr_result.get("result", {}).get("text", "")
                or ocr_result.get("data", {}).get("extracted_text", "")
                or str(ocr_result)
            )
            return {
                "ocr_payload": ocr_result, 
                "extracted_text": extracted,
                "error": None, 
                "current_step": "ocr"
            }
              
        return {"error": f"OCR API Error: {response.text}", "current_step": "ocr"}
        
    except Exception as e:
        return {"error": f"Failed to contact ocr_service: {str(e)}", "current_step": "ocr"}