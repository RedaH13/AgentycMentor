import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os
import glob

# --- 1. Setup ---
JSON_DIR = "test/submissions/"
OUTPUT_DIR = "analytics/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- 2. Data Extraction ---
all_words = []
tesseract_files_count = 0
gemini_files_count = 0

json_files = glob.glob(os.path.join(JSON_DIR, "*.json"))
print(f"Scanning {len(json_files)} JSON files for engine comparison...")

for file_path in json_files:
    fname = os.path.basename(file_path).lower()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            ocr_data = json.load(f)
            
        raw_engine = str(ocr_data.get("source_engine") or "").strip().lower()
        
        # Determine engine: check source_engine field first, then fallback to filename
        if "gemini" in raw_engine or "_gemini" in fname:
            engine = "Gemini"
            gemini_files_count += 1
        elif "tesseract" in raw_engine or raw_engine in ["auto", ""]:
            engine = "Tesseract"
            tesseract_files_count += 1
        else:
            continue
            
        for page in ocr_data.get("pages", []):
            for line in page.get("lines", []):
                for word in line.get("words", []):
                    conf = word.get("confidence")
                    if conf is not None:
                        all_words.append({
                            "Engine": engine,
                            "Confidence": float(conf)
                        })
    except Exception as e:
        print(f"Failed to process {file_path}: {e}")

print(f"Identified Tesseract files: {tesseract_files_count}")
print(f"Identified Gemini files:    {gemini_files_count}")
print(f"Total word tokens parsed:   {len(all_words)}")
df = pd.DataFrame(all_words)

if df.empty:
    print("No valid Tesseract or Gemini confidence data found. Run your tests first!")
    exit(1)

for eng in df["Engine"].unique():
    subset = df[df["Engine"] == eng]["Confidence"]
    print(f"[{eng}] Words: {len(subset)} | Mean Conf: {subset.mean():.2f}% | Median: {subset.median():.2f}%")

# --- 3. Chart Generation (KDE Plot) ---
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(10, 6))

# Plot intersecting density curves
sns.kdeplot(
    data=df,
    x="Confidence",
    hue="Engine",
    fill=True,
    common_norm=False,
    palette={"Tesseract": "#b1ee5c", "Gemini": "#4f46e5"},
    alpha=0.5,
    linewidth=2,
    ax=ax
)

# Add dashed lines for the averages
engines = df["Engine"].unique()
for engine in engines:
    avg = df[df["Engine"] == engine]["Confidence"].mean()
    color = "#f59e0b" if engine == "Tesseract" else "#4f46e5"
    ax.axvline(avg, color=color, linestyle='dashed', linewidth=2.5, 
               label=f"{engine} Avg ({avg:.1f}%)")

# Formatting
ax.set_title('OCR Confidence Distribution: Tesseract vs. Gemini AI', fontsize=15, fontweight='bold', pad=15)
ax.set_xlabel('Word-Level Confidence Score (%)', fontsize=12, fontweight='bold')
ax.set_ylabel('Density (Frequency of Words)', fontsize=12, fontweight='bold')
ax.set_xlim(0, 100)

# Clean up legend
ax.legend(frameon=True, shadow=True, fontsize=11, loc='upper left')

fig.tight_layout()

# Save
output_path = os.path.join(OUTPUT_DIR, "03_engine_comparison_kde.pdf")
plt.savefig(output_path, format='pdf', dpi=300)
plt.savefig(output_path.replace('.pdf', '.png'), format='png', dpi=300)

print(f"📊 Engine comparison chart saved to {output_path}")