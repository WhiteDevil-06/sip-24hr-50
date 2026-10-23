"""
Phase 4: LSTM Model Architecture for Soil Moisture Forecasting
Project: Deep Learning-Based Soil Moisture Prediction for Smart Irrigation
Target: SM_50cm at t + 96 steps (24 hours ahead)
Input: Sequence of 96 historical steps (24 hours) with N features.

LSTM Architectural Principles:
1. Long Short-Term Memory (LSTM) cells maintain a cell state (C_t) that preserves long-term
   hydraulic history across 96 time steps without vanishing gradients.
2. Forget Gate (f_t): Regulates how much of the previous cell state to discard.
3. Input Gate (i_t): Determines which new sensory information to store into the cell state.
4. Output Gate (o_t): Controls how much of the updated cell state to pass into the hidden state (h_t).
5. Dense Projection Head: Projects final recurrent representation into scalar SM_50cm prediction.
"""

import torch
import torch.nn as nn


class SoilMoistureLSTM(nn.Module):
    """
    Modular LSTM neural network for 24-hour ahead soil moisture forecasting.
    """

    def __init__(
        self,
        input_size: int = 1,
        hidden_size: int = 64,
        num_layers: int = 2,
        dropout: float = 0.2,
    ):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        # LSTM Layer
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )

        # Non-linear Dense Regression Head
        self.regressor = nn.Sequential(
            nn.Linear(hidden_size, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        Args:
            x: Input tensor of shape [batch_size, seq_len=96, input_size]
        Returns:
            Output prediction tensor of shape [batch_size]
        """
        # lstm_out shape: [batch_size, seq_len, hidden_size]
        lstm_out, _ = self.lstm(x)

        # Extract representation from the final time-step of the sequence
        last_step_repr = lstm_out[:, -1, :]  # [batch_size, hidden_size]

        # Project through regression head
        prediction = self.regressor(last_step_repr)  # [batch_size, 1]

        return prediction.squeeze(-1)  # [batch_size]
