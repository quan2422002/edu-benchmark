"""Conversion helpers from audited raw dialogues to benchmark samples."""
"""Deterministic raw-dialogue to benchmark-candidate conversion."""

from .pipeline import run_conversion_input_build, run_conversion_pilot

__all__ = ["run_conversion_input_build", "run_conversion_pilot"]
