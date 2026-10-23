"""
Phase 1: Exploratory Data Analysis - Step 2: Temporal Regularity, Lags & Statistics
Computes:
1. Exact timestamp delta distribution (verifying 15-minute frequency = 96 steps/day).
2. Missing interval quantification across all years.
3. Summary statistics for SM_50cm, SM_5cm, Temp_50cm, Temp_5cm, and Precipitation.
4. Hydraulic infiltration lag: Cross-correlation between SM_5cm/Rainfall and SM_50cm.
"""

from pathlib import Path
import pandas as pd
import numpy as np

DATA_RAW_DIR = Path("data/raw")
csv_files = sorted(DATA_RAW_DIR.glob("*_V1.csv"))

print("=== 1. TIMESTAMP REGULARITY & DELTA ANALYSIS ===")
total_records = 0
delta_counts = {}

dfs = []
for f in csv_files:
    df = pd.read_csv(f, na_values=["NaN", "NA", ""])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)
    
    # Calculate time delta between consecutive rows
    deltas = df["timestamp"].diff().dropna()
    for delta, count in deltas.value_counts().items():
        delta_str = str(delta)
        delta_counts[delta_str] = delta_counts.get(delta_str, 0) + count
        
    dfs.append(df)
    total_records += len(df)

print(f"Total rows analyzed across 10 years: {total_records:,}")
print("Top time deltas between consecutive rows:")
for d, c in sorted(delta_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
    pct = (c / (total_records - len(csv_files))) * 100
    print(f"  Delta {d}: {c:,} times ({pct:.2f}%)")

# Combine common features
common_cols = ["timestamp", "SM_50cm", "SM_5cm", "Temp_50cm", "Temp_5cm", "Precipitation"]
df_all = pd.concat([d[[c for c in common_cols if c in d.columns]] for d in dfs], ignore_index=True)
for col in ["SM_50cm", "SM_5cm", "Temp_50cm", "Temp_5cm", "Precipitation"]:
    df_all[col] = pd.to_numeric(df_all[col], errors="coerce")

print("\n=== 2. OVERALL STATISTICAL PROFILE (2016-2025) ===")
stats = df_all[["SM_50cm", "SM_5cm", "Temp_50cm", "Temp_5cm", "Precipitation"]].describe().T
stats["missing_%"] = df_all[["SM_50cm", "SM_5cm", "Temp_50cm", "Temp_5cm", "Precipitation"]].isna().mean() * 100
print(stats[["count", "mean", "std", "min", "25%", "50%", "75%", "max", "missing_%"]].to_string())

# Modern period profile (2022-2025)
df_modern = df_all[df_all["timestamp"] >= "2022-01-01"].copy()
print("\n=== 3. MODERN INSTRUMENTATION PROFILE (2022-2025) ===")
stats_modern = df_modern[["SM_50cm", "SM_5cm", "Temp_50cm", "Temp_5cm", "Precipitation"]].describe().T
stats_modern["missing_%"] = df_modern[["SM_50cm", "SM_5cm", "Temp_50cm", "Temp_5cm", "Precipitation"]].isna().mean() * 100
print(stats_modern[["count", "mean", "std", "min", "25%", "50%", "75%", "max", "missing_%"]].to_string())

print("\n=== 4. HYDRAULIC INFILTRATION LAG ANALYSIS ===")
# Cross-correlation between SM_5cm and SM_50cm on clean 2022-2024 data
df_clean = df_all[(df_all["timestamp"] >= "2022-01-01") & (df_all["timestamp"] < "2025-01-01")].copy()
df_clean = df_clean.dropna(subset=["SM_50cm", "SM_5cm", "Precipitation"])

# Calculate lag correlation from 0 to 192 steps (0 to 48 hours in 15-min increments)
lags = [0, 4, 8, 16, 32, 64, 96, 128, 160, 192] # 0h, 1h, 2h, 4h, 8h, 16h, 24h, 32h, 40h, 48h
print("Autocorrelation of SM_50cm with past values:")
for lag in lags:
    corr = df_clean["SM_50cm"].autocorr(lag=lag)
    hours = lag * 0.25
    print(f"  Lag {lag:3d} steps ({hours:4.1f} hours): correlation = {corr:.4f}")

print("\nCross-correlation between SM_5cm(t - lag) and SM_50cm(t):")
for lag in lags:
    shifted_sm5 = df_clean["SM_5cm"].shift(lag)
    corr = df_clean["SM_50cm"].corr(shifted_sm5)
    hours = lag * 0.25
    print(f"  SM_5cm lead by {lag:3d} steps ({hours:4.1f} hours): correlation = {corr:.4f}")
