#!/usr/bin/env python3
"""Prepare namespaced round-2 inputs for an approved Plan 03 v5-family audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from loguru import logger

from edu_benchmark.dialogue_audit.v5_input_preparation import (
    prepare_v5_inputs_from_config,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--log-file", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.log_file.parent.mkdir(parents=True, exist_ok=True)
    logger.remove()
    logger.add(
        args.log_file,
        level="INFO",
        backtrace=True,
        diagnose=False,
        colorize=False,
        enqueue=False,
    )
    try:
        result = prepare_v5_inputs_from_config(
            args.config,
            overwrite=args.overwrite,
        )
    except Exception:
        logger.exception("Plan 03 v5-family input preparation failed")
        raise SystemExit(1) from None
    logger.info(
        "Plan 03 v5-family input preparation completed summary={}",
        json.dumps(result, ensure_ascii=False, sort_keys=True),
    )


if __name__ == "__main__":
    main()
