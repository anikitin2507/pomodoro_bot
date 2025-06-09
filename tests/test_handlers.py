"""Tests for the Pomodoro bot handlers."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.handlers.command_handlers import parse_pomodoro_args


def test_parse_pomodoro_args_default():
    """Test parsing pomodoro arguments with default values."""
    # Empty args should return defaults
    work, break_ = parse_pomodoro_args([])
    assert work == 25
    assert break_ == 5


def test_parse_pomodoro_args_valid():
    """Test parsing pomodoro arguments with valid values."""
    # Valid args
    work, break_ = parse_pomodoro_args(["30", "10"])
    assert work == 30
    assert break_ == 10

    # Only work minutes
    work, break_ = parse_pomodoro_args(["45"])
    assert work == 45
    assert break_ == 5  # Default


def test_parse_pomodoro_args_invalid():
    """Test parsing pomodoro arguments with invalid values."""
    # Invalid args should use defaults
    work, break_ = parse_pomodoro_args(["invalid", "10"])
    assert work == 25  # Default
    assert break_ == 10

    work, break_ = parse_pomodoro_args(["30", "invalid"])
    assert work == 30
    assert break_ == 5  # Default

    # Negative values should use defaults
    work, break_ = parse_pomodoro_args(["-10", "10"])
    assert work == 25  # Default
    assert break_ == 10 