import cv2
import numpy as np
import io
from PIL import Image

def preprocess_image(image_array: np.ndarray) -> np.ndarray:
    """
    Optimizes a numpy image array for Tesseract OCR.
    """
    # 1. Convert to grayscale if it's a color image
    if len(image_array.shape) == 3:
        gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
    else:
        gray = image_array

    # 2. Noise Removal
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # 3. Adaptive Thresholding
    thresh = cv2.adaptiveThreshold(
        blur, 
        255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 
        11, # Block size
        2   # Constant subtracted from the mean
    )

    # Optional: If handwriting is too faint, adding morphological operations (dilation) here.
    # kernel = np.ones((2,2), np.uint8)
    # thresh = cv2.erode(thresh, kernel, iterations=1)

    return thresh

def compress_image_bytes(file_bytes: bytes, max_size_mb: float = 1.9) -> bytes:
    """
    Iteratively compresses an image byte stream to ensure it stays under the max_size_mb limit.
    Ideal for strict API constraints (like OCR.Space's 2MB limit).
    """
    max_size_bytes = int(max_size_mb * 1024 * 1024)
    
    # If it's already under the limit, return immediately
    if len(file_bytes) <= max_size_bytes:
        return file_bytes

    image = Image.open(io.BytesIO(file_bytes))
    
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
        
    quality = 95
    current_bytes = file_bytes
    
    # Iteratively reduce quality and dimensions until it fits
    while len(current_bytes) > max_size_bytes and quality > 10:
        output = io.BytesIO()
        
        # Slightly scale down the resolution at each pass to help compression
        width, height = image.size
        image = image.resize((int(width * 0.9), int(height * 0.9)), Image.Resampling.LANCZOS)
        
        # Save to buffer with new quality
        image.save(output, format="JPEG", quality=quality, optimize=True)
        current_bytes = output.getvalue()
        
        # Drop quality aggressively for the next loop if still too large
        quality -= 15 
        
    return current_bytes