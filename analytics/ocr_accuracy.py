import json
import matplotlib.pyplot as plt
import numpy as np
import os
import glob
from matplotlib.patches import Patch

# File Paths
json_dir = "test/submissions/"
output_dir = "analytics/outputs"
os.makedirs(output_dir, exist_ok=True)

# Data Extraction
word_confidences = []
global_confidences = []

# Find all JSON files in the directory
json_files = glob.glob(os.path.join(json_dir, "*.json"))

if not json_files:
    print(f"Error: No JSON files found in {json_dir}.")
    exit(1)

print(f"Scanning {len(json_files)} submission files...")

for file_path in json_files:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            ocr_data = json.load(f)
            
        global_conf = ocr_data.get("global_confidence")
        if global_conf is not None:
            global_confidences.append(float(global_conf))
        
        # Drill down into the JSON schema to get every word's confidence
        for page in ocr_data.get("pages", []):
            for line in page.get("lines", []):
                for word in line.get("words", []):
                    conf = word.get("confidence")
                    if conf is not None:
                        word_confidences.append(float(conf))
                        
    except Exception as e:
        print(f"Failed to process {file_path}: {str(e)}")

if not word_confidences:
    print("No word confidences found in any of the JSON files.")
    exit(1)

# Calculate aggregate metrics
avg_global_confidence = sum(global_confidences) / len(global_confidences) if global_confidences else 0.0
avg_global_confidence = round(avg_global_confidence, 2)

# Categorize for Reporting
high_conf = sum(1 for c in word_confidences if c >= 80)
med_conf = sum(1 for c in word_confidences if 50 <= c < 80)
low_conf = sum(1 for c in word_confidences if c < 50)
total_words = len(word_confidences)

print(f"\n--- Aggregate Results ---")
print(f"Analyzed {total_words} total words across {len(json_files)} documents.")
print(f"High (>80%): {high_conf} words")
print(f"Medium (50-79%): {med_conf} words")
print(f"Low (<50%): {low_conf} words")
print(f"Average Global Confidence: {avg_global_confidence}%")

# Generate the Histogram
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(9, 6))

# Plot the distribution of word confidences in 10-point bins
counts, bins, patches = ax.hist(word_confidences, bins=10, range=(0, 100), 
                                edgecolor='white', linewidth=1.2)

# Color-code the bins (Red for Low, Yellow for Med, Green for High)
for i, patch in enumerate(patches):
    if bins[i] < 50:
        patch.set_facecolor("#c92424") # Red
    elif bins[i] < 80:
        patch.set_facecolor("#df9008b0") # Amber
    else:
        patch.set_facecolor("#21aa7c") # Green

# Add a vertical line for the Average Global Confidence
ax.axvline(avg_global_confidence, color='#1e3a8a', linestyle='dashed', linewidth=2.5, 
           label=f'Avg Global Confidence ({avg_global_confidence}%)')

# Formatting
ax.set_title(f'Aggregate OCR Confidence Distribution (n={len(json_files)} Submissions)', 
             fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Tesseract Confidence Score (%)', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Words', fontsize=12, fontweight='bold')
ax.set_xticks(np.arange(0, 101, 10))

legend_elements = [
    Patch(facecolor='#21aa7c', label=f'High Certainty ({high_conf} words)'),
    Patch(facecolor='#df9008b0', label=f'Medium Certainty ({med_conf} words)'),
    Patch(facecolor='#c92424', label=f'Low Certainty / Guesses ({low_conf} words)'),
    ax.lines[0]
]
ax.legend(handles=legend_elements, frameon=True, shadow=True, fontsize=10, loc='upper left')

fig.tight_layout()

# Save outputs
output_path = os.path.join(output_dir, "01_ocr_aggregate_confidence_distribution.pdf")
plt.savefig(output_path, format='pdf', dpi=300)
plt.savefig(output_path.replace('.pdf', '.png'), format='png', dpi=300)
print(f"\nChart successfully saved to {output_path}")