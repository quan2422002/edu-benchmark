#!/usr/bin/env python
"""Create the non-destructive repository inventory for Plan 06."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from edu_benchmark.repository_hygiene import (
    HygieneConfigError,
    load_hygiene_config,
    scan_repository,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inventory repository outputs without deleting or moving files"
    )
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    try:
        config = load_hygiene_config(args.config)
        result = scan_repository(config)
    except (HygieneConfigError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
