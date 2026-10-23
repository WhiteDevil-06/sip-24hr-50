"""
Phase 1: Exploratory Data Analysis (EDA) & Dataset Audit
Project: Deep Learning-Based Soil Moisture Prediction for Smart Irrigation
Target Variable: SM_50cm (Soil moisture at 50 cm depth in % Volumetric Water Content)
Resolution: 15-minute intervals (96 steps per 24 hours)

Author: Project Lead (Guided by Antigravity)
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# 1. Setup paths safely using pathlib (avoiding hardcoded OS backslashes)
DATA_RAW_DIR = Path("data/raw")

print("=" * 70)
print("STEP 1: INSPECTING YEARLY DATASET FILES & SCHEMAS (2016–2025)")
print("=" * 70)

# Check all available CSV files in data/raw/
csv_files = sorted(DATA_RAW_DIR.glob("*_V1.csv"))
print(f"Found {len(csv_files)} annual CSV files in '{DATA_RAW_DIR}'.\n")

# Store summary records for comparison
summary_records = []

for filepath in csv_files:
    year_str = filepath.stem.split("_")[0]
    
    # Read CSV: parse string "NaN" directly with na_values for speed
    df = pd.read_csv(filepath, na_values=["NaN", "NA", ""])
    
    # Parse timestamp as datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    # Basic dimensions
    n_rows, n_cols = df.shape
    start_time = df["timestamp"].min()
    end_time = df["timestamp"].max()
    
    # Target variable (SM_50cm) audit
    has_target = "SM_50cm" in df.columns
    if has_target:
        # Convert to numeric in case of mixed types
        sm50 = pd.to_numeric(df["SM_50cm"], errors="coerce")
        missing_count = sm50.isna().sum()
        missing_pct = (missing_count / n_rows) * 100.0
        min_val = sm50.min()
        max_val = sm50.max()
        mean_val = sm50.mean()
    else:
        missing_count, missing_pct, min_val, max_val, mean_val = np.nan, np.nan, np.nan, np.nan, np.nan
        
    summary_records.append({
        "Year": year_str,
        "Rows": n_rows,
        "Columns": n_cols,
        "Start Date": start_time.strftime("%Y-%m-%d"),
        "End Date": end_time.strftime("%Y-%m-%d"),
        "SM_50cm Missing %": round(missing_pct, 1) if has_target else "N/A",
        "SM_50cm Min (%)": round(min_val, 2) if has_target else "N/A",
        "SM_50cm Mean (%)": round(mean_val, 2) if has_target else "N/A",
        "SM_50cm Max (%)": round(max_val, 2) if has_target else "N/A",
    })

# Convert to DataFrame for clean tabular display
summary_df = pd.DataFrame(summary_records)
print(summary_df.to_string(index=False))

print("\n" + "=" * 70)
print("STEP 2: COMMON COLUMNS ACROSS ALL YEARS")
print("=" * 70)

# Inspect column names across all files to find common features
all_columns = {}
for filepath in csv_files:
    cols = pd.read_csv(filepath, nrows=1).columns.tolist()
    all_columns[filepath.stem] = cols

# Find intersection of all column sets
common_cols = set.intersection(*[set(c) for c in all_columns.values()])
print(f"Features present in ALL 10 years ({len(common_cols)} columns):")
for col in sorted(common_cols):
    print(f"  - {col}")

print("\nAll columns present per year:")
for yr, cols in all_columns.items():
    print(f"  {yr}: {cols}")
