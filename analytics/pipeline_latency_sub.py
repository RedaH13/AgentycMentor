import os
import glob
import json
import matplotlib.pyplot as plt
import numpy as np

# --- 1. Setup ---
BENCHMARK_DIR = "analytics/outputs/benchmarks"
OUTPUT_DIR = "analytics/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Grab all benchmark JSON files and sort them to keep the order consistent
files = sorted(glob.glob(os.path.join(BENCHMARK_DIR, "*.json")))

if not files:
    print(f"No benchmark files found in '{BENCHMARK_DIR}'.")
    exit(1)

print(f"Found {len(files)} benchmark files. Generating latency chart...")

# --- 2. Data Extraction ---
stage_order = [
    ("ocr", "OCR Ingestion", "#540d6e"),
    ("rag_retrieve", "RAG Retrieval", "#ee4266"),
    ("diagnostic", "Diagnostic Agent", "#f7d6e0"),
    ("guidance", "Guidance Agent", "#ffd23f"),
    ("correction", "Correction Agent", "#3bceac"),
    ("feedback", "Feedback Agent", "#9871f1"),
]

runs = []
stage_times = {stage_key: [] for stage_key, _, _ in stage_order}

for idx, fpath in enumerate(files):
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        t = data.get("timings", {})
        runs.append(f"Submission {idx + 1}")
        for stage_key, _, _ in stage_order:
            # Fallback to 0.0 if a stage is missing for some reason
            stage_times[stage_key].append(t.get(stage_key, 0.0))
            
    except Exception as e:
        print(f"Error reading {fpath}: {e}")

# --- 3. Chart Generation ---
plt.style.use("seaborn-v0_8-whitegrid")
# Increased height (8) to comfortably fit 10 or more rows
fig, ax = plt.subplots(figsize=(12, 8))

y_pos = np.arange(len(runs))
left_offset = np.zeros(len(runs))

for stage_key, label_name, color in stage_order:
    vals = np.array(stage_times[stage_key])
    ax.barh(y_pos, vals, left=left_offset, height=0.6, label=label_name, color=color, edgecolor="white")
    
    # Add text labels inside the segments
    for i, (v, left) in enumerate(zip(vals, left_offset)):
        # Only annotate if the segment is wide enough (>= 1.5 seconds) to avoid text overlap
        if v >= 1.5:
            ax.text(left + v / 2, i, f"{v:.1f}s", ha="center", va="center", color="white", fontsize=8.5, fontweight="bold")
            
    left_offset += vals

# Annotate the total execution time at the far right of each bar
for i, total in enumerate(left_offset):
    ax.text(total + 0.5, i, f"{total:.1f}s total", ha="left", va="center", color="#1f2937", fontsize=10, fontweight="bold")

# Formatting
ax.set_yticks(y_pos)
ax.set_yticklabels(runs, fontsize=11)
ax.invert_yaxis()  # Put Submission 1 at the top
ax.set_xlabel("Latency (Seconds)", fontsize=12, fontweight="bold", labelpad=10)
ax.set_title(f"End-to-End Pipeline Latency Breakdown (n={len(files)})", fontsize=14, fontweight="bold", pad=15)

# Dynamically scale X-axis to give the total labels room to breathe
ax.set_xlim(0, max(left_offset) + max(left_offset) * 0.15)

# Place the legend in the bottom right
ax.legend(loc="lower right", frameon=True, shadow=True, fontsize=10)

fig.tight_layout()

# --- 4. Save Outputs ---
output_png = os.path.join(OUTPUT_DIR, "04_pipeline_latency.png")
output_pdf = os.path.join(OUTPUT_DIR, "04_pipeline_latency.pdf")

plt.savefig(output_png, dpi=300)
plt.savefig(output_pdf, format="pdf", dpi=300)

print(f"Chart successfully saved to {output_png}")