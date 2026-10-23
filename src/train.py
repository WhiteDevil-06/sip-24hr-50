"""
Phase 4 & 5: Model Training, Early Stopping, and Evaluation Pipeline
Project: Deep Learning-Based Soil Moisture Prediction for Smart Irrigation
"""

from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.optim.lr_scheduler import ReduceLROnPlateau

from src.model import SoilMoistureLSTM
from src.metrics import compute_metrics


class SoilMoistureDataset(Dataset):
    """
    PyTorch Dataset wrapper for 3D time-series input tensors and scalar targets.
    """

    def __init__(self, X: np.ndarray, y: np.ndarray):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32)

    def __len__(self) -> int:
        return len(self.X)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.X[idx], self.y[idx]


def train_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
) -> float:
    """Trains model for one epoch and returns average training loss."""
    model.train()
    total_loss = 0.0

    for X_batch, y_batch in loader:
        X_batch, y_batch = X_batch.to(device), y_batch.to(device)

        optimizer.zero_grad()
        preds = model(X_batch)
        loss = criterion(preds, y_batch)
        loss.backward()

        # Gradient clipping to prevent gradient explosion in recurrent layers
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

        total_loss += loss.item() * len(X_batch)

    return total_loss / len(loader.dataset)


def validate_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> float:
    """Evaluates model on validation loader and returns average validation loss."""
    model.eval()
    total_loss = 0.0

    with torch.no_grad():
        for X_batch, y_batch in loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            preds = model(X_batch)
            loss = criterion(preds, y_batch)
            total_loss += loss.item() * len(X_batch)

    return total_loss / len(loader.dataset)


def train_lstm_model(
    model: SoilMoistureLSTM,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    epochs: int = 10,
    batch_size: int = 512,
    lr: float = 0.001,
    patience: int = 3,
    stride: int = 2,
    checkpoint_path: Path = Path("models/best_model.pt"),
    device: Optional[torch.device] = None,
) -> Dict[str, List[float]]:
    """
    Executes model training with Early Stopping and learning rate reduction.
    Saves the best model state dict whenever validation loss improves.
    """
    if device is None:
        device = torch.device("cpu")

    model.to(device)
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

    # Subsample training data by stride (e.g. stride=2 takes every 30 min window)
    # Reduces 99% auto-correlated duplicate windows while preserving full seasonal coverage
    if stride > 1:
        X_train_sub = X_train[::stride]
        y_train_sub = y_train[::stride]
    else:
        X_train_sub = X_train
        y_train_sub = y_train

    train_dataset = SoilMoistureDataset(X_train_sub, y_train_sub)
    val_dataset = SoilMoistureDataset(X_val, y_val)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    scheduler = ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=1)

    history = {"train_loss": [], "val_loss": []}
    best_val_loss = float("inf")
    patience_counter = 0

    print(f"\nStarting LSTM training on device: {device}", flush=True)
    print(f"Training samples (stride={stride}): {len(X_train_sub):,}, Validation samples: {len(X_val):,}", flush=True)
    print(f"Batches per epoch: {len(train_loader)} train, {len(val_loader)} val (batch_size={batch_size})", flush=True)
    print("-" * 75, flush=True)

    for epoch in range(1, epochs + 1):
        train_loss = train_epoch(model, train_loader, criterion, optimizer, device)
        val_loss = validate_epoch(model, val_loader, criterion, device)
        scheduler.step(val_loss)

        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)

        # Early Stopping & Checkpointing
        is_best = val_loss < best_val_loss
        if is_best:
            best_val_loss = val_loss
            patience_counter = 0
            torch.save(model.state_dict(), checkpoint_path)
            flag = "(* Checkpoint Saved)"
        else:
            patience_counter += 1
            flag = ""

        current_lr = optimizer.param_groups[0]["lr"]
        print(f"Epoch {epoch:02d}/{epochs:02d} | Train MSE: {train_loss:.6f} | Val MSE: {val_loss:.6f} | LR: {current_lr:.6f} {flag}", flush=True)

        if patience_counter >= patience:
            print(f"\nEarly stopping triggered after {epoch} epochs (val loss did not improve for {patience} epochs).", flush=True)
            break

    # Reload best weights
    model.load_state_dict(torch.load(checkpoint_path, map_location=device))
    print(f"Loaded best checkpoint with Validation MSE = {best_val_loss:.6f}", flush=True)
    return history


def evaluate_lstm_model(
    model: SoilMoistureLSTM,
    X: np.ndarray,
    y: np.ndarray,
    target_scaler=None,
    batch_size: int = 256,
    device: Optional[torch.device] = None,
) -> Tuple[Dict[str, float], np.ndarray]:
    """
    Evaluates LSTM model on a given dataset.
    Inverts predictions to physical units (% VWC) using target_scaler before computing metrics.
    """
    if device is None:
        device = torch.device("cpu")

    model.eval()
    model.to(device)

    dataset = SoilMoistureDataset(X, y)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

    preds_list = []
    with torch.no_grad():
        for X_batch, _ in loader:
            X_batch = X_batch.to(device)
            p = model(X_batch)
            preds_list.append(p.cpu().numpy())

    preds = np.concatenate(preds_list, axis=0)

    if target_scaler is not None:
        y_pred_unscaled = target_scaler.inverse_transform(preds.reshape(-1, 1)).flatten()
        y_true_unscaled = target_scaler.inverse_transform(y.reshape(-1, 1)).flatten()
    else:
        y_pred_unscaled = preds
        y_true_unscaled = y

    metrics = compute_metrics(y_true_unscaled, y_pred_unscaled)
    return metrics, y_pred_unscaled
