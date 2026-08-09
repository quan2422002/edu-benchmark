#!/usr/bin/env python3
"""Compatibility entry point for config-driven Section V analysis."""

from __future__ import annotations

import sys

from edu_benchmark.experiment_runtime.cli import main as runtime_main


if __name__ == "__main__":
    raise SystemExit(runtime_main(["run", *sys.argv[1:]]))
