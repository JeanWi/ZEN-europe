"""Unit tests for the argument handling of the ZEN-europe CLI.

Generating a dataset is covered by the end-to-end tests; these cover the
combinations the CLI accepts and the command it builds for a subprocess.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pytest

from zen_europe.cli import _command_for, zen_europe_cli


def _run_cli(monkeypatch: pytest.MonkeyPatch, *args: str) -> None:
    """Invoke the CLI with the given arguments."""
    monkeypatch.setattr(sys, "argv", ["zen-europe", *args])
    zen_europe_cli()


def test_all_and_model_cannot_be_combined(monkeypatch: pytest.MonkeyPatch) -> None:
    """Building every variant and naming one are mutually exclusive."""
    with pytest.raises(SystemExit):
        _run_cli(monkeypatch, "--all", "--model", "late_start")


def test_sequential_requires_all(monkeypatch: pytest.MonkeyPatch) -> None:
    """--sequential has no meaning for a single dataset."""
    with pytest.raises(SystemExit):
        _run_cli(monkeypatch, "--sequential")


def test_jobs_requires_all(monkeypatch: pytest.MonkeyPatch) -> None:
    """--jobs has no meaning for a single dataset."""
    with pytest.raises(SystemExit):
        _run_cli(monkeypatch, "--jobs", "2")


def test_all_without_a_models_file_is_reported(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """--all needs a models file and says so when there is none."""
    config_path = tmp_path / "config.yaml"
    config_path.write_text("settings: {}\n", encoding="utf-8")

    with pytest.raises(FileNotFoundError, match="Could not find the models file"):
        _run_cli(monkeypatch, "--all", "--config_path", str(config_path))


def test_command_reuses_this_interpreter(tmp_path: Path) -> None:
    """A subprocess runs the interpreter of this process, not the PATH one."""
    args = argparse.Namespace(config_path=None, output_path=tmp_path / "out")
    models_path = tmp_path / "models.yaml"

    command = _command_for("late_start", args, models_path)

    assert command[0] == sys.executable
    assert command[1:3] == ["-m", "zen_europe"]
    assert "--model" in command
    assert command[command.index("--model") + 1] == "late_start"
    assert command[command.index("--models_path") + 1] == str(models_path)
    assert "--config_path" not in command


def test_command_passes_an_explicit_config(tmp_path: Path) -> None:
    """A config given to --all is handed on to each subprocess."""
    config_path = tmp_path / "config.yaml"
    args = argparse.Namespace(config_path=config_path, output_path=tmp_path / "out")

    command = _command_for("base", args, tmp_path / "models.yaml")

    assert command[command.index("--config_path") + 1] == str(config_path)
