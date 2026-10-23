"""
Pure-Python Fast Statistical Dataset Audit across all 10 years (2016-2025).
No external libraries needed - zero import overhead and runs in ~1 second.
"""
import csv
import sys
from pathlib import Path
from datetime import datetime
from collections import Counter
import math

DATA_RAW_DIR = Path("data/raw")
csv_files = sorted(DATA_RAW_DIR.glob("*_V1.csv"))

print("=" * 80, flush=True)
print("PHASE 1: STATISTICAL AUDIT ACROSS 10 YEARS (2016-2025)", flush=True)
print("=" * 80, flush=True)

all_years_summary = []
global_deltas = Counter()
total_rows = 0

# For modern period (2022-2024) autocorrelation & cross-correlation:
# We collect chronological (sm50, sm5, precip)
timeseries_clean = []

for f in csv_files:
    year_str = f.stem.split("_")[0]
    with open(f, mode="r", encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        fieldnames = reader.fieldnames or []
        
        has_sm50 = "SM_50cm" in fieldnames
        has_sm5 = "SM_5cm" in fieldnames
        
        sm50_vals = []
        sm50_missing = 0
        row_count = 0
        first_ts = None
        last_ts = None
        prev_dt = None
        
        for row in reader:
            row_count += 1
            total_rows += 1
            ts_str = row.get("timestamp", "").strip()
            
            # Timestamp parsing
            if ts_str:
                dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                if first_ts is None:
                    first_ts = dt
                last_ts = dt
                
                if prev_dt is not None:
                    delta_min = (dt - prev_dt).total_seconds() / 60.0
                    global_deltas[delta_min] += 1
                prev_dt = dt
                
                # Check SM_50cm
                v_str = row.get("SM_50cm", "").strip()
                if v_str in ("", "NaN", "NA", "null", "E36", "E6"):
                    sm50_missing += 1
                    sm_val = None
                else:
                    try:
                        sm_val = float(v_str)
                        sm50_vals.append(sm_val)
                    except ValueError:
                        sm50_missing += 1
                        sm_val = None
                
                # Also collect clean timeseries for 2022-2024 lag study
                if "2022" <= year_str <= "2024":
                    sm5_str = row.get("SM_5cm", "").strip()
                    try:
                        v5 = float(sm5_str) if sm5_str not in ("", "NaN", "NA") else None
                    except ValueError:
                        v5 = None
                    timeseries_clean.append((sm_val, v5))
            else:
                sm50_missing += 1
                
        # Stats for SM_50cm
        if sm50_vals:
            n = len(sm50_vals)
            mean_v = sum(sm50_vals) / n
            var_v = sum((x - mean_v) ** 2 for x in sm50_vals) / (n - 1) if n > 1 else 0
            std_v = math.sqrt(var_v)
            min_v = min(sm50_vals)
            max_v = max(sm50_vals)
        else:
            mean_v = std_v = min_v = max_v = float("nan")
            
        miss_pct = (sm50_missing / row_count * 100.0) if row_count else 100.0
        
        all_years_summary.append({
            "year": year_str,
            "rows": row_count,
            "cols": len(fieldnames),
            "start": first_ts.strftime("%Y-%m-%d") if first_ts else "N/A",
            "end": last_ts.strftime("%Y-%m-%d") if last_ts else "N/A",
            "sm50_miss_pct": miss_pct,
            "sm50_min": min_v,
            "sm50_mean": mean_v,
            "sm50_max": max_v,
            "sm50_std": std_v,
            "columns": fieldnames,
        })

import traceback

try:
    print(f"{'Year':<6} | {'Rows':<7} | {'Start':<10} | {'End':<10} | {'SM_50cm Miss%':<14} | {'Min':<6} | {'Mean':<6} | {'Max':<6} | {'Std':<6}", flush=True)
    print("-" * 80, flush=True)
    for s in all_years_summary:
        print(f"{s['year']:<6} | {s['rows']:<7} | {s['start']:<10} | {s['end']:<10} | {s['sm50_miss_pct']:>13.1f}% | {s['sm50_min']:>6.2f} | {s['sm50_mean']:>6.2f} | {s['sm50_max']:>6.2f} | {s['sm50_std']:>6.2f}", flush=True)
except Exception as e:
    traceback.print_exc()

print("\n" + "=" * 80, flush=True)
print(f"TOTAL ROWS PROCESSED: {total_rows:,}", flush=True)
print("TIMESTAMP DELTA DISTRIBUTION (Top intervals):", flush=True)
for d, count in global_deltas.most_common(5):
    pct = (count / (total_rows - len(csv_files))) * 100.0
    print(f"  Delta = {d:6.1f} minutes: {count:>8,} occurrences ({pct:.2f}%)", flush=True)

# Autocorrelation of SM_50cm in modern period (2022-2024)
print("\n" + "=" * 80, flush=True)
print("AUTOCORRELATION & HYDRAULIC INFILTRATION PROFILE (2022-2024)", flush=True)
print("=" * 80, flush=True)

# Compute mean and variance for series
valid_sm50 = [x[0] for x in timeseries_clean if x[0] is not None]
if valid_sm50:
    mean_50 = sum(valid_sm50) / len(valid_sm50)
    var_50 = sum((x - mean_50) ** 2 for x in valid_sm50) / len(valid_sm50)
    
    lags = [0, 4, 8, 16, 32, 64, 96, 128, 160, 192]
    print(f"{'Lag Steps':<10} | {'Lag Time':<10} | {'SM_50cm Autocorrelation':<24}", flush=True)
    print("-" * 50, flush=True)
    for lag in lags:
        cov = 0
        n_pairs = 0
        for i in range(len(timeseries_clean) - lag):
            v1 = timeseries_clean[i][0]
            v2 = timeseries_clean[i + lag][0]
            if v1 is not None and v2 is not None:
                cov += (v1 - mean_50) * (v2 - mean_50)
                n_pairs += 1
        autocorr = (cov / n_pairs) / var_50 if n_pairs and var_50 else 0
        hours = lag * 0.25
        print(f"{lag:<10} | {hours:>6.1f} h    | {autocorr:>23.4f}", flush=True)

# Cross correlation: SM_5cm(t - lag) with SM_50cm(t)
valid_sm5 = [x[1] for x in timeseries_clean if x[1] is not None]
if valid_sm5 and valid_sm50:
    mean_5 = sum(valid_sm5) / len(valid_sm5)
    var_5 = sum((x - mean_5) ** 2 for x in valid_sm5) / len(valid_sm5)
    std_5 = math.sqrt(var_5)
    std_50 = math.sqrt(var_50)
    
    print("\n" + "-" * 50, flush=True)
    print(f"{'Lead Steps':<10} | {'Lead Time':<10} | {'Cross-Corr: SM_5cm(t-lag) vs SM_50cm(t)':<35}", flush=True)
    print("-" * 60, flush=True)
    for lag in lags:
        cov = 0
        n_pairs = 0
        for i in range(len(timeseries_clean) - lag):
            v_sm5 = timeseries_clean[i][1]       # at t - lag
            v_sm50 = timeseries_clean[i + lag][0] # at t
            if v_sm5 is not None and v_sm50 is not None:
                cov += (v_sm5 - mean_5) * (v_sm50 - mean_50)
                n_pairs += 1
        crosscorr = (cov / n_pairs) / (std_5 * std_50) if n_pairs and std_5 and std_50 else 0
        hours = lag * 0.25
        print(f"{lag:<10} | {hours:>6.1f} h    | {crosscorr:>35.4f}", flush=True)

print("\nAUDIT COMPLETE.", flush=True)
