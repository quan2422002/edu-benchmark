#!/usr/bin/env python3
"""Validate or run the authenticated Plan 04 learning-resource portal."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from edu_benchmark.review_delivery import (
    build_portal_catalog,
    load_review_products_config,
    serve_portal,
)
from edu_benchmark.review_delivery.portal import (
    PortalDataError,
    credentials_from_environment,
    write_portal_validation,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--host")
    parser.add_argument("--port", type=int)
    parser.add_argument(
        "--allow-network-bind",
        action="store_true",
        help="Required when binding to anything other than 127.0.0.1.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_review_products_config(args.config, repository_root=REPOSITORY_ROOT)
    host = args.host or config.portal.host
    port = args.port or config.portal.port
    if host != "127.0.0.1" and not args.allow_network_bind:
        raise PortalDataError(
            "Refusing non-loopback bind without --allow-network-bind and a separately "
            "approved network deployment configuration"
        )
    if args.validate_only:
        catalog = build_portal_catalog(config)
        path = write_portal_validation(config, catalog)
        print(json.dumps({**catalog.validation, "validation_output": str(path)}, ensure_ascii=False, indent=2))
        return
    username, password = credentials_from_environment(config.portal)
    serve_portal(
        config,
        username=username,
        password=password,
        host=host,
        port=port,
    )


if __name__ == "__main__":
    main()
