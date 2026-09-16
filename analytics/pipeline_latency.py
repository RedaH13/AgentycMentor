import os
import glob
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- 1. Setup ---
BENCHMARK_DIR = "analytics/outputs/benchmarks"
OUTPUT_DIR = "analytics/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

files = glob.glob(os.path.join(BENCHMARK_DIR, "*.json"))

if not files:
    print(f"No benchmark files found in '{BENCHMARK_DIR}'.")
    exit(1)

# --- 2. Data Extraction ---
stage_mapping = {
    "ocr": "1. OCR Ingestion",
    "rag_retrieve": "2. RAG Retrieval",
    "diagnostic": "3. Diagnostic",
    "guidance": "4. Guidance",
    "correction": "5. Correction",
    "feedback": "6. Feedback"
}

data = []

for fpath in files:
    with open(fpath, "r", encoding="utf-8") as f:
        log = json.load(f)
    
    timings = log.get("timings", {})
    for raw_key, formatted_name in stage_mapping.items():
        if raw_key in timings:
            data.append({
                "Pipeline Stage": formatted_name,
                "Latency (Seconds)": timings[raw_key]
            })

df = pd.DataFrame(data)

if df.empty:
    print("No valid timing metrics found in the JSON files.")
    exit(1)

# --- 3. Chart Generation ---
plt.style.use("seaborn-v0_8-whitegrid")
fig, ax = plt.subplots(figsize=(12, 6))

# Custom color palette
colors = ["#3b82f6", "#06b6d4", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"]

# Create the Box Plot (Shows median, quartiles, and range)
sns.boxplot(
    data=df, 
    x="Pipeline Stage", 
    y="Latency (Seconds)", 
    palette=colors,
    width=0.5,
    boxprops=dict(alpha=0.7, edgecolor='gray'),
    medianprops=dict(color="black", linewidth=2),
    flierprops=dict(marker='o', color='red', markersize=5),
    ax=ax
)

# Overlay the Swarm Plot (Shows the actual 10 individual runs)
sns.swarmplot(
    data=df, 
    x="Pipeline Stage", 
    y="Latency (Seconds)", 
    color=".2",
    size=6,
    alpha=0.8,
    ax=ax
)

# Formatting
ax.set_title(f"Multi-Agent Pipeline Latency Distribution (n={len(files)} Submissions)", 
             fontsize=15, fontweight="bold", pad=15)
ax.set_xlabel("Agent / Execution Node", fontsize=12, fontweight="bold", labelpad=10)
ax.set_ylabel("Execution Latency (Seconds)", fontsize=12, fontweight="bold", labelpad=10)

# Calculate and annotate average latency above each box
means = df.groupby("Pipeline Stage")["Latency (Seconds)"].mean()
for i, stage in enumerate(stage_mapping.values()):
    if stage in means:
        ax.text(i, df["Latency (Seconds)"].max() * 1.05, f"Avg: {means[stage]:.1f}s", 
                ha="center", va="bottom", fontsize=10, fontweight="bold", color="#374151")

# Expand Y-axis slightly to fit the text annotations
ax.set_ylim(0, df["Latency (Seconds)"].max() * 1.15)

fig.tight_layout()

# --- 4. Save Outputs ---
output_pdf = os.path.join(OUTPUT_DIR, "04_pipeline_latency_boxplot.pdf")
plt.savefig(output_pdf, format="pdf", dpi=300, bbox_inches="tight")
plt.savefig(output_pdf.replace(".pdf", ".png"), format="png", dpi=300, bbox_inches="tight")

print(f"Latency distribution chart successfully saved to {output_pdf}")