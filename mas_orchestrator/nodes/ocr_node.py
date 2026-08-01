import requests
import os
from mas_orchestrator.state.schemas import MASState

def run_ocr_node(state: MASState) -> dict:
    """Delegates perception to the independent ocr_service"""
    file_path = state.get("file_path")
    
    if not file_path or not os.path.exists(file_path):
        return {"error": "No valid file_path provided to OCR node"}

    try:
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f, "image/jpeg")}
            response = requests.post("http://127.0.0.1:8000/api/v1/ocr/extract", files=files)
            
        if response.status_code == 200:
            return {"ocr_payload": response.json(), "error": None, "current_step": "ocr"}
        return {"error": f"OCR API Error: {response.text}", "current_step": "ocr"}
        
    except Exception as e:
        return {"error": f"Failed to contact ocr_service: {str(e)}", "current_step": "ocr"}