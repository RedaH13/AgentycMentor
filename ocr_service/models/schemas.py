from pydantic import BaseModel, Field
from typing import List, Optional

class BoundingBox(BaseModel):
    """Spatial coordinates for image-based text blocks."""
    x: float
    y: float
    width: float
    height: float

class WordBlock(BaseModel):
    """Granular word-level data."""
    text: str
    box: Optional[BoundingBox] = None
    confidence: Optional[float] = None # Native to Tesseract

class LineBlock(BaseModel):
    """Line-level data grouping multiple words."""
    line_text: str
    words: List[WordBlock] = Field(default_factory=list)
    box: Optional[BoundingBox] = None

class PageBlock(BaseModel):
    """Handles multi-page PDFs or single images."""
    page_number: int = 1
    lines: List[LineBlock] = Field(default_factory=list)

class OCRDatabaseRecord(BaseModel):
    """The root payload to be saved to your database."""
    # Metadata
    file_name: str = Field(default="unknown")
    is_image: bool = Field(default=False)
    source_engine: str = Field(default="", description="e.g., 'tesseract', 'gemini', 'pdfplumber'")
    global_confidence: float = Field(default=100.0)
    
    # Payload
    full_text: str = Field(default="")
    pages: List[PageBlock] = Field(default_factory=list)
    
    # Error Handling
    error: Optional[str] = None