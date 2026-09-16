import json
import matplotlib.pyplot as plt
import numpy as np
import os
import glob

# Metric Calculators
def levenshtein_distance(s1, s2):
    if len(s1) < len(s2): return levenshtein_distance(s2, s1)
    if len(s2) == 0: return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

def calculate_cer(raw_text, true_text):
    if len(true_text) == 0: return 0.0
    distance = levenshtein_distance(list(raw_text), list(true_text))
    return min((distance / len(true_text)) * 100, 100.0)

def calculate_wer(raw_text, true_text):
    raw_words = raw_text.split()
    true_words = true_text.split()
    if len(true_words) == 0: return 0.0
    distance = levenshtein_distance(raw_words, true_words)
    return min((distance / len(true_words)) * 100, 100.0)

# Dynamic Data Processing
SUBMISSIONS_DIR = "test/submissions/"
OUTPUT_DIR = "analytics/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Auto find all corrected text files
txt_files = glob.glob(os.path.join(SUBMISSIONS_DIR, "*_corrected.txt"))

if not txt_files:
    print("No ground truth text files found. Please create files ending in '_corrected.txt'.")
    exit(1)

metrics = {"cer": [], "wer": [], "labels": []}

print(f"Scanning {len(txt_files)} ground truth files...")

for txt_path in txt_files:
    base_name = os.path.basename(txt_path).replace("_corrected.txt", "")
    json_path = os.path.join(SUBMISSIONS_DIR, f"{base_name}.json")
    
    if not os.path.exists(json_path):
        print(f"Warning: Missing JSON prediction for {base_name}. Skipping.")
        continue
        
    try:
        # Read Prediction
        with open(json_path, "r", encoding="utf-8") as f:
            ocr_data = json.load(f)
            raw_text = ocr_data.get("full_text", "")
            
        # Read Ground Truth
        with open(txt_path, "r", encoding="utf-8") as f:
            true_text = f.read().strip()
            
        # Calculate
        cer = calculate_cer(raw_text, true_text)
        wer = calculate_wer(raw_text, true_text)
        
        metrics["labels"].append(base_name)
        metrics["cer"].append(cer)
        metrics["wer"].append(wer)
        
        print(f"Processed {base_name} -> CER: {cer:.1f}% | WER: {wer:.1f}%")
        
    except Exception as e:
        print(f"Error processing {base_name}: {e}")

if not metrics["labels"]:
    print("No valid data pairs processed. Exiting.")
    exit(1)

# Chart Generation
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(12, 6))

x = np.arange(len(metrics["labels"]))
width = 0.35

rects1 = ax.bar(x - width/2, metrics["cer"], width, label='CER (%)', color="#5b53eec2")
rects2 = ax.bar(x + width/2, metrics["wer"], width, label='WER (%)', color="#42e42dae")

ax.set_ylabel('Error Rate (%)', fontsize=12, fontweight='bold')
ax.set_title('OCR Accuracy: CER & WER Across Submissions', fontsize=14, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(metrics["labels"], fontsize=10, rotation=30, ha="right")
ax.legend(frameon=True, shadow=True, fontsize=11)

# Dynamically scale Y-axis
ax.set_ylim(0, max(max(metrics["cer"]), max(metrics["wer"])) + 15) 

# Data Labels
def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height:.1f}%',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3), 
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, fontweight='bold')

autolabel(rects1)
autolabel(rects2)

fig.tight_layout()

# Save
output_path = os.path.join(OUTPUT_DIR, "02_ocr_cer_wer_analysis.pdf")
plt.savefig(output_path, format='pdf', dpi=300)
plt.savefig(output_path.replace('.pdf', '.png'), format='png', dpi=300)
print(f"\nCER/WER Chart successfully saved to {output_path}")