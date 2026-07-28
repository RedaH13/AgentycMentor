import io
import pytesseract
from pytesseract import Output
import pdfplumber
import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
from google import genai
from google.genai import types
import json
from core.preprocessor import preprocess_image
from core.postprocessor import clean_text
from config.settings import settings
from core.preprocessor import compress_image_bytes
from models.schemas import OCRDatabaseRecord, PageBlock, LineBlock, WordBlock, BoundingBox

def process_pdf(file_bytes: bytes, filename: str = "unknown"):
    # Extracts text from digital PDFs (professor rubrics).
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)        
        if not text.strip():
            text = extract_with_fitz(file_bytes)            
        record = OCRDatabaseRecord(
            file_name=filename,
            is_image=False,
            source_engine="pdfplumber",
            global_confidence=100.0,
            full_text=clean_text(text),
            pages=[]
        )
        return record.model_dump()
    except Exception as e:
        return {"error": f"PDF processing failed: {str(e)}"}
    
def extract_with_fitz(file_bytes: bytes):
    # Fallback using PyMuPDF
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text("text")
    return text

def parse_ocrspace_to_schema(raw_json: dict) -> list:
    """Translates OCR.Space's native JSON into PageBlock schema."""
    pages = []
    for result in raw_json.get("ParsedResults", []):
        page = PageBlock(lines=[])
        overlay = result.get("TextOverlay") or {}
        for line_data in overlay.get("Lines", []):
            words = []
            for w_data in line_data.get("Words", []):
                words.append(WordBlock(
                    text=w_data.get("WordText", ""),
                    box=BoundingBox(
                        x=w_data.get("Left", 0),
                        y=w_data.get("Top", 0),
                        width=w_data.get("Width", 0),
                        height=w_data.get("Height", 0)
                    )
                ))
            # OCR.Space provides MinTop and MaxHeight, we need to calculate min_x and max_x from the words.
            min_y = line_data.get("MinTop", 0)
            max_h = line_data.get("MaxHeight", 0)
            min_x = min([w.box.x for w in words]) if words else 0
            max_x = max([w.box.x + w.box.width for w in words]) if words else 0
            line = LineBlock(
                line_text=" ".join(w.text for w in words),
                words=words,
                box=BoundingBox(x=min_x, y=min_y, width=max_x-min_x, height=max_h))
            page.lines.append(line)
        pages.append(page)        
    return pages

def parse_tesseract_to_schema(ocr_data: dict) -> list:
    """Translates Tesseract's image_to_data dictionary into PageBlock schema."""
    page = PageBlock(lines=[])
    lines_dict = {}
    # Group words by their line number
    for i, text in enumerate(ocr_data['text']):
        conf = int(ocr_data['conf'][i])
        # Skip empty blocks (-1 confidence) or whitespace
        if conf == -1 or not text.strip():
            continue
            
        line_num = ocr_data['line_num'][i]
        if line_num not in lines_dict:
            lines_dict[line_num] = []          
        lines_dict[line_num].append(WordBlock(
            text=text,
            confidence=float(conf),
            box=BoundingBox(
                x=float(ocr_data['left'][i]),
                y=float(ocr_data['top'][i]),
                width=float(ocr_data['width'][i]),
                height=float(ocr_data['height'][i])
            )
        ))       
    # Construct LineBlocks from the grouped words
    for line_num, words in lines_dict.items():
        if not words: 
            continue         
        min_x = min([w.box.x for w in words])
        min_y = min([w.box.y for w in words])
        max_w = max([w.box.x + w.box.width for w in words]) - min_x
        max_h = max([w.box.y + w.box.height for w in words]) - min_y        
        page.lines.append(LineBlock(
            line_text=" ".join([w.text for w in words]),
            words=words,
            box=BoundingBox(x=min_x, y=min_y, width=max_w, height=max_h)
        ))        
    return [page]

def process_image(file_bytes: bytes, filename: str = "unknown", ocr_engine: str = "auto"):
    """
    Extracts text from student submissions (images). ocr_engine options: 
      - "auto": Tesseract first, fallback to Gemini if confidence < 70
      - "tesseract": Forces local OCR only
      - "gemini": Forces Gemini API only
      - "ocrspace": Forces OCR.Space API only
    """
    try:
        if ocr_engine == "tesseract" or ocr_engine == "auto":
            image = Image.open(io.BytesIO(file_bytes))        
            processed = preprocess_image(np.array(image))

            ocr_data = pytesseract.image_to_data(processed, output_type=Output.DICT)
            valid_scores = [int(c) for c in ocr_data['conf'] if int(c) != -1]
            confidence = sum(valid_scores) / len(valid_scores) if valid_scores else 0
            
            raw_text = pytesseract.image_to_string(processed)
            
            if ocr_engine == "auto" and confidence < 50:
                fallback_provider = "ocrspace" # Defaulting to OCR.Space for the spatial JSON
                safe_bytes = compress_image_bytes(file_bytes, max_size_mb=1.9)
                result_record = call_cloud_ocr(safe_bytes, filename, provider=fallback_provider)
                return result_record.model_dump()
            else:
                # Use Tesseract adapter
                pages = parse_tesseract_to_schema(ocr_data)
                record = OCRDatabaseRecord(
                    file_name=filename,
                    is_image=True,
                    source_engine="tesseract",
                    global_confidence=round(confidence, 2),
                    full_text=clean_text(raw_text),
                    pages=pages
                )
                return record.model_dump()

        elif ocr_engine in ["gemini", "ocrspace"]:
            safe_bytes = compress_image_bytes(file_bytes, max_size_mb=1.9)
            result_record = call_cloud_ocr(safe_bytes, filename, provider=ocr_engine)
            return result_record.model_dump()

    except Exception as e:
        return {"error": f"Image processing failed: {str(e)}"}

def call_cloud_ocr(file_bytes: bytes, filename: str, provider: str = "ocrspace") -> OCRDatabaseRecord:
    if provider == "ocrspace":
        import requests
        api_key = settings.OCRSPACE_API_KEY
        resp = requests.post(
            "https://api.ocr.space/parse/image",
            files={"file": (filename, file_bytes, "image/jpeg")},
            data={"language": "eng", "isOverlayRequired": "true"},
            headers={"apikey": api_key}
        )
        
        result_json = resp.json()
        pages = parse_ocrspace_to_schema(result_json)
        
        # Extract full raw text safely
        parsed_results = result_json.get("ParsedResults", [{}])
        full_text = parsed_results[0].get("ParsedText", "") if parsed_results else ""

        return OCRDatabaseRecord(
            file_name=filename,
            is_image=True,
            source_engine="ocrspace",
            global_confidence=100.0,
            full_text=clean_text(full_text),
            pages=pages
        )

    elif provider == "gemini":
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        prompt = """
        Extract all text and mathematical formulas from this image. 
        Return a JSON object with a single key 'lines', containing an array of line objects. 
        Each line object must have 'line_text', 'ymin', 'xmin', 'ymax', 'xmax', and an array of 'words'. 
        Each word object must have 'text', 'ymin', 'xmin', 'ymax', 'xmax'.
        """
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                genai.types.Part.from_bytes(data=file_bytes, mime_type="image/jpeg"),
                prompt
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        pages = []
        full_text_parts = []
        
        # 3. Parse Gemini's JSON and map it to our DB Schema
        try:
            gemini_data = json.loads(response.text)
            page = PageBlock(lines=[])
            
            for line_data in gemini_data.get("lines", []):
                words = []
                for w_data in line_data.get("words", []):
                    words.append(WordBlock(
                        text=w_data.get("text", ""),
                        box=BoundingBox(
                            x=float(w_data.get("xmin", 0)),
                            y=float(w_data.get("ymin", 0)),
                            width=float(w_data.get("xmax", 0)) - float(w_data.get("xmin", 0)),
                            height=float(w_data.get("ymax", 0)) - float(w_data.get("ymin", 0))
                        )
                    ))
                
                line_obj = LineBlock(
                    line_text=line_data.get("line_text", ""),
                    words=words,
                    box=BoundingBox(
                        x=float(line_data.get("xmin", 0)),
                        y=float(line_data.get("ymin", 0)),
                        width=float(line_data.get("xmax", 0)) - float(line_data.get("xmin", 0)),
                        height=float(line_data.get("ymax", 0)) - float(line_data.get("ymin", 0))
                    )
                )
                page.lines.append(line_obj)
                full_text_parts.append(line_obj.line_text)
                
            pages = [page]
            full_text = "\n".join(full_text_parts)
            
        except (json.JSONDecodeError, TypeError, ValueError):
            # Safe fallback just in case the JSON parsing fails
            full_text = response.text
            pages = []

        return OCRDatabaseRecord(
            file_name=filename,
            is_image=True,
            source_engine="gemini",
            global_confidence=100.0,
            full_text=clean_text(full_text),
            pages=pages
        )
