"""
Unit tests for Phase 4: SoilMoistureLSTM architecture
"""

import pytest
import numpy as np
import torch
from src.model import SoilMoistureLSTM


def test_lstm_forward_pass_univariate():
    # Batch size 4, sequence length 96, input features 1
    batch_size = 4
    seq_len = 96
    input_size = 1

    model = SoilMoistureLSTM(input_size=input_size, hidden_size=32, num_layers=1)
    dummy_input = torch.randn(batch_size, seq_len, input_size)

    output = model(dummy_input)

    # Output must be a 1D tensor of shape [batch_size]
    assert output.shape == (batch_size,), f"Expected shape ({batch_size},), got {output.shape}"
    assert torch.isfinite(output).all(), "Model output contains non-finite values (NaN or Inf)"


def test_lstm_forward_pass_multivariate():
    # Batch size 8, sequence length 96, input features 5
    batch_size = 8
    seq_len = 96
    input_size = 5

    model = SoilMoistureLSTM(input_size=input_size, hidden_size=64, num_layers=2, dropout=0.2)
    dummy_input = torch.randn(batch_size, seq_len, input_size)

    output = model(dummy_input)

    assert output.shape == (batch_size,)
    assert torch.isfinite(output).all()
