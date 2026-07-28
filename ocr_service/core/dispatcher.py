import mimetypes
from core.engine import process_pdf, process_image

def dispatch(filename: str, file_bytes: bytes, ocr_engine: str = "auto") -> dict:
    # Routes the uploaded file to the correct processing pipeline
    mime_type, _ = mimetypes.guess_type(filename)

    if mime_type == "application/pdf":
        return process_pdf(file_bytes, filename)
    
    elif mime_type and mime_type.startswith("image/"):
        return process_image(file_bytes, ocr_engine=ocr_engine)
    
    else:
        raise ValueError(f"Unsupported file type: {mime_type}. Please upload a PDF or an Image.")