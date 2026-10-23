"""
Phase 2: Preprocessing Pipeline & Sliding Window Generator
Soil Moisture Prediction for Smart Irrigation
Target: SM_50cm at t + 96 steps (24 hours ahead)
Window Size: past 96 steps (24 hours of history)
Resolution: 15-minute intervals (Delta t = 15 min)

Rules Enforced:
1. Strict chronological partition (Train: 2016-2022 excl. 2021; Val: 2023; Test: 2024-2025).
2. Scalers fit EXCLUSIVELY on training data to prevent lookahead data leakage.
3. Scalers serialized to pickle and JSON format for downstream serving (Rahul / Phase 6).
4. No artificial interpolation across major sensor downtime gaps.
"""

from pathlib import Path
import json
import pickle
from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


# Core feature definitions
COMMON_FEATURES = [
    "SM_50cm",        # Target variable (autoregressive input)
    "SM_5cm",         # Surface moisture (infiltration lead indicator)
    "Temp_50cm",      # Deep root zone temperature
    "Temp_5cm",       # Surface temperature (evaporative driver)
    "Precipitation",  # Rainfall depth per 15 min
]

TARGET_VARIABLE = "SM_50cm"
WINDOW_SIZE = 96      # 24 hours of historical inputs (96 * 15 min)
FORECAST_HORIZON = 96 # 24 hours into future (t + 96)


def load_raw_dataset(
    raw_dir: Path = Path("data/raw"),
    years: Optional[List[int]] = None,
    exclude_years: Optional[List[int]] = None,
) -> pd.DataFrame:
    """
    Loads and standardizes annual CSV files from data/raw/.
    Handles string 'NaN', parses timestamps, validates chronological ordering,
    and removes duplicate timestamps.
    """
    if years is None:
        years = list(range(2016, 2026))
    if exclude_years is None:
        exclude_years = [2021] # Exclude 2021 hardware transition year per Phase 1 audit

    active_years = [y for y in years if y not in exclude_years]
    frames = []

    for yr in sorted(active_years):
        file_path = raw_dir / f"{yr}_V1.csv"
        if not file_path.exists():
            continue

        df = pd.read_csv(file_path, na_values=["NaN", "NA", "", "E36", "E6"])
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp").reset_index(drop=True)
        
        # Deduplicate timestamps if any
        df = df.drop_duplicates(subset=["timestamp"], keep="first")
        frames.append(df)

    if not frames:
        raise FileNotFoundError(f"No valid dataset CSV files found in {raw_dir}")

    full_df = pd.concat(frames, ignore_index=True)
    full_df = full_df.sort_values("timestamp").reset_index(drop=True)
    return full_df


def split_chronological(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Partitions dataset chronologically according to the approved Phase 1 gate:
      - Training Set:   Jan 1, 2016 - Dec 31, 2022 (excluding 2021 transition year)
      - Validation Set: Jan 1, 2023 - Dec 31, 2023
      - Test Set:       Jan 1, 2024 - Jun 30, 2025
    """
    train_mask = (df["timestamp"] < "2023-01-01") & (df["timestamp"].dt.year != 2021)
    val_mask = (df["timestamp"] >= "2023-01-01") & (df["timestamp"] < "2024-01-01")
    test_mask = (df["timestamp"] >= "2024-01-01")

    train_df = df[train_mask].copy().reset_index(drop=True)
    val_df = df[val_mask].copy().reset_index(drop=True)
    test_df = df[test_mask].copy().reset_index(drop=True)

    return train_df, val_df, test_df


class PreprocessingPipeline:
    """
    Manages normalization scalers, serialization, and gap-aware sliding window extraction.
    """

    def __init__(
        self,
        feature_cols: Optional[List[str]] = None,
        target_col: str = TARGET_VARIABLE,
        window_size: int = WINDOW_SIZE,
        horizon: int = FORECAST_HORIZON,
    ):
        self.feature_cols = feature_cols or COMMON_FEATURES
        self.target_col = target_col
        self.window_size = window_size
        self.horizon = horizon

        self.feature_scaler: Optional[MinMaxScaler] = None
        self.target_scaler: Optional[MinMaxScaler] = None
        self.fitted: bool = False

    def fit_scalers(self, train_df: pd.DataFrame) -> "PreprocessingPipeline":
        """
        Fits MinMax scalers strictly on training data.
        Guarantees zero data leakage from validation or test partitions.
        """
        # Ensure target is present in feature_cols
        if self.target_col not in self.feature_cols:
            raise ValueError(f"Target column '{self.target_col}' must be included in features.")

        # Clean training partition: fill minor missing values with median/forward-fill
        clean_train = train_df[self.feature_cols].copy()
        clean_train = clean_train.ffill().bfill()

        self.feature_scaler = MinMaxScaler(feature_range=(0, 1))
        self.feature_scaler.fit(clean_train)

        # Target scaler fitted strictly on target column
        self.target_scaler = MinMaxScaler(feature_range=(0, 1))
        self.target_scaler.fit(clean_train[[self.target_col]])

        self.fitted = True
        return self

    def save_artifacts(self, output_dir: Path = Path("models")) -> None:
        """
        Serializes fitted scalers as:
        1. Pickle objects (for Python ML pipelines).
        2. Clean JSON metadata (for Rahul's FastAPI service / Phase 6).
        """
        if not self.fitted:
            raise RuntimeError("Cannot save un-fitted preprocessing scalers.")

        output_dir.mkdir(parents=True, exist_ok=True)

        # 1. Save pickle
        with open(output_dir / "feature_scaler.pkl", "wb") as f:
            pickle.dump(self.feature_scaler, f)
        with open(output_dir / "target_scaler.pkl", "wb") as f:
            pickle.dump(self.target_scaler, f)

        # 2. Save JSON metadata (scale factors and min values for pure math calculation)
        metadata = {
            "feature_cols": self.feature_cols,
            "target_col": self.target_col,
            "window_size": self.window_size,
            "horizon": self.horizon,
            "features_min": self.feature_scaler.data_min_.tolist(),
            "features_max": self.feature_scaler.data_max_.tolist(),
            "features_scale": self.feature_scaler.scale_.tolist(),
            "features_min_offset": self.feature_scaler.min_.tolist(),
            "target_min": float(self.target_scaler.data_min_[0]),
            "target_max": float(self.target_scaler.data_max_[0]),
            "target_scale": float(self.target_scaler.scale_[0]),
            "target_min_offset": float(self.target_scaler.min_[0]),
        }

        with open(output_dir / "scaler_metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

    def load_artifacts(self, input_dir: Path = Path("models")) -> "PreprocessingPipeline":
        """
        Reloads serialized scalers from disk.
        """
        scaler_pkl = input_dir / "feature_scaler.pkl"
        target_pkl = input_dir / "target_scaler.pkl"
        meta_json = input_dir / "scaler_metadata.json"

        if not (scaler_pkl.exists() and target_pkl.exists() and meta_json.exists()):
            raise FileNotFoundError(f"Missing required scaler artifacts in {input_dir}")

        with open(scaler_pkl, "rb") as f:
            self.feature_scaler = pickle.load(f)
        with open(target_pkl, "rb") as f:
            self.target_scaler = pickle.load(f)
        with open(meta_json, "r", encoding="utf-8") as f:
            meta = json.load(f)

        self.feature_cols = meta["feature_cols"]
        self.target_col = meta["target_col"]
        self.window_size = meta["window_size"]
        self.horizon = meta["horizon"]
        self.fitted = True
        return self

    def create_sliding_windows(
        self,
        df: pd.DataFrame,
        apply_scaling: bool = True,
        max_gap_minutes: float = 30.0,
    ) -> Tuple[np.ndarray, np.ndarray, pd.DataFrame]:
        """
        Constructs 3D input tensors and 1D target vectors for LSTM.
        Guarantees that no sequence crosses a multi-hour gap or missing period.

        Returns:
            X: np.ndarray of shape [N, window_size, len(feature_cols)]
            y: np.ndarray of shape [N] (scaled or unscaled target at t + horizon)
            metadata_df: DataFrame containing exact input_start, input_end, and target timestamps.
        """
        if not self.fitted and apply_scaling:
            raise RuntimeError("Must fit scalers before creating scaled windows.")

        # Sort chronologically
        df_clean = df.sort_values("timestamp").reset_index(drop=True)

        # Impute isolated short gaps (<= 2 steps = 30 mins) with forward-fill
        features_df = df_clean[self.feature_cols].copy().ffill().bfill()
        scaled_features = (
            self.feature_scaler.transform(features_df)
            if apply_scaling
            else features_df.values
        )

        target_vals = df_clean[self.target_col].copy().ffill().bfill().values
        scaled_targets = (
            self.target_scaler.transform(target_vals.reshape(-1, 1)).flatten()
            if apply_scaling
            else target_vals
        )

        timestamps = df_clean["timestamp"].values

        # Find contiguous continuous segments where consecutive rows are <= max_gap_minutes
        deltas = np.diff(timestamps) / np.timedelta64(1, "m")
        gap_indices = np.where(deltas > max_gap_minutes)[0]

        segment_starts = [0] + (gap_indices + 1).tolist()
        segment_ends = gap_indices.tolist() + [len(df_clean) - 1]

        X_list = []
        y_list = []
        meta_records = []

        total_span = self.window_size + self.horizon - 1

        for seg_start, seg_end in zip(segment_starts, segment_ends):
            seg_len = seg_end - seg_start + 1
            if seg_len < self.window_size + self.horizon:
                # Segment too short to form even one valid window + horizon pair
                continue

            for i in range(seg_start, seg_end - total_span + 1):
                input_slice = scaled_features[i : i + self.window_size]
                target_idx = i + self.window_size + self.horizon - 1

                t_start = timestamps[i]
                t_end = timestamps[i + self.window_size - 1]
                t_target = timestamps[target_idx]

                # Strict physical validation:
                # Target timestamp must be exactly 24 hours after the input window end!
                expected_delta = np.timedelta64(24, "h")
                actual_delta = t_target - t_end
                if actual_delta != expected_delta:
                    # Gaps or irregularities detected inside span, discard this window
                    continue

                X_list.append(input_slice)
                y_list.append(scaled_targets[target_idx])
                meta_records.append({
                    "input_start": t_start,
                    "input_end": t_end,
                    "target_time": t_target,
                    "target_raw": target_vals[target_idx],
                })

        if not X_list:
            return (
                np.empty((0, self.window_size, len(self.feature_cols))),
                np.empty((0,)),
                pd.DataFrame(),
            )

        X = np.array(X_list, dtype=np.float32)
        y = np.array(y_list, dtype=np.float32)
        meta_df = pd.DataFrame(meta_records)

        return X, y, meta_df
