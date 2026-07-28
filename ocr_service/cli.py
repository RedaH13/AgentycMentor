import argparse
import json
import os
from core.dispatcher import dispatch

def main():
    parser = argparse.ArgumentParser(description="Test the MAS OCR Extraction Pipeline.")
    parser.add_argument("filepath", type=str, help="Path to the PDF or Image file")
    parser.add_argument(
        "--engine", 
        type=str, 
        choices=["auto", "tesseract", "gemini", "ocrspace"], 
        default="auto",
        help="Specify the OCR engine for images (default: auto)"
    )
    parser.add_argument(
        "--outdir", 
        type=str, 
        default="test",
        help="Directory to save the output text and JSON files (default: test)"
    )

    args = parser.parse_args()
    if not os.path.exists(args.filepath):
        print(f"Error: File '{args.filepath}' not found.")
        return

    filename = os.path.basename(args.filepath)
    base_name, _ = os.path.splitext(filename)
    os.makedirs(args.outdir, exist_ok=True)

    with open(args.filepath, "rb") as f:
        file_bytes = f.read()

    print(f"Processing '{filename}' using engine '{args.engine}'...")

    try:
        result = dispatch(filename, file_bytes, args.engine)
        
        source_engine = str(result.get("source_engine", "unknown")).upper()
        full_text = result.get("full_text", "")

        json_path = os.path.join(args.outdir, f"{base_name}_{args.engine}.json")
        with open(json_path, "w", encoding="utf-8") as jf:
            json.dump(result, jf, indent=2, ensure_ascii=False)
        
        text_path = os.path.join(args.outdir, f"{base_name}_{args.engine}.txt")
        with open(text_path, "w", encoding="utf-8") as tf:
            tf.write(f"### OCR Engine: {source_engine}\n")
            tf.write(f"Global Confidence: {result.get('global_confidence', 0)}%\n\n")
            tf.write(full_text)

        print(f"\nSuccess! Results saved to:\n- {json_path}\n- {text_path}")
        print(f"Model utilized: {source_engine}")
        
    except Exception as e:
        print(f"\nPipeline Error: {str(e)}")

if __name__ == "__main__":
    main()