import matplotlib.pyplot as plt
import numpy as np
import os

# --- 1. Setup ---
output_dir = "analytics/outputs"
os.makedirs(output_dir, exist_ok=True)

# --- 2. The Evaluation Data ---
evaluations = {
    "dotnet1": {"TP": 3, "FP": 2, "FN": 1},
    "sql8": {"TP": 5, "FP": 3, "FN": 3},
    "sql10": {"TP": 4, "FP": 1, "FN": 1},
    "dotnet4": {"TP": 5, "FP": 2, "FN": 0},
    "sql12": {"TP": 6, "FP": 3, "FN": 2},
    "dotnet5": {"TP": 4, "FP": 1, "FN": 1},
    "sql22": {"TP": 4, "FP": 2, "FN": 2},
    "sql13": {"TP": 3, "FP": 1, "FN": 1}
}

labels = list(evaluations.keys())
precision_scores = []
recall_scores = []
f1_scores = []

# --- 3. Calculate Metrics ---
for sub in labels:
    tp = evaluations[sub]["TP"]
    fp = evaluations[sub]["FP"]
    fn = evaluations[sub]["FN"]
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    precision_scores.append(precision * 100)
    recall_scores.append(recall * 100)
    f1_scores.append(f1 * 100)

# --- 4. Grouped Bar Chart Generation ---
plt.style.use("seaborn-v0_8-whitegrid")
fig, ax = plt.subplots(figsize=(12, 6))

x = np.arange(len(labels))
width = 0.25

rects1 = ax.bar(x - width, precision_scores, width, label='Precision (Accuracy of Flags)', color="#f0d078")
rects2 = ax.bar(x, recall_scores, width, label='Recall (Detection Rate)', color="#3e7ce1b0")
rects3 = ax.bar(x + width, f1_scores, width, label='F1-Score (Harmonic Mean)', color="#0e9f6e")

# Formatting
ax.set_ylabel('Score (%)', fontsize=12, fontweight='bold')
ax.set_title('Correction Agent Performance: Error Detection Accuracy', fontsize=14, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=11, fontweight='medium', rotation=30, ha='right')
ax.set_ylim(0, 115)
# Moved legend to top left to avoid covering the 0% data labels at the bottom
ax.legend(loc='upper left', frameon=True, shadow=True, fontsize=10)

# Data Labels
def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height:.0f}%',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3), 
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, fontweight='bold')

autolabel(rects1)
autolabel(rects2)
autolabel(rects3)

fig.tight_layout()

# Save Outputs
output_pdf = os.path.join(output_dir, "05_critical_error_metrics.pdf")
plt.savefig(output_pdf, format="pdf", dpi=300)
plt.savefig(output_pdf.replace(".pdf", ".png"), format="png", dpi=300)

print(f"Precision/Recall Scorecard saved to {output_pdf}")