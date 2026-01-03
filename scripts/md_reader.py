"""Standalone entrypoint for the embedded MONARCH Markdown reader."""
from __future__ import annotations

import argparse
from pathlib import Path

from killchain_cli import DEFAULT_DOC_ROOT, browse_markdown


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read Markdown files from ops_docs/")
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_DOC_ROOT,
        help="Root directory to scan for Markdown files (default: ops_docs/)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    browse_markdown(args.root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
