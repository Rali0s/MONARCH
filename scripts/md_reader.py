"""Interactive Markdown reader for MONARCH ops documentation.

This utility scans ``ops_docs/`` for Markdown files gathered from external
ethical-hacking repositories and offers a simple menu to open and read each
file. Files are displayed in sorted order to make navigation predictable.
"""
from __future__ import annotations

import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DOC_ROOT = PROJECT_ROOT / "ops_docs"


def collect_markdown_files(root: Path) -> list[Path]:
    """Return a sorted list of Markdown files beneath ``root``."""

    if not root.exists():
        return []

    return sorted(
        (path for path in root.rglob("*.md") if path.is_file()),
        key=lambda path: path.relative_to(root).as_posix().lower(),
    )


def print_menu(files: list[Path], root: Path) -> None:
    """Display the available Markdown files for selection."""

    print("\n=== MONARCH Markdown Reader ===")
    print(f"Source root: {root}")
    if not files:
        print("No Markdown files found. Populate ops_docs/ with fetch_external_docs.py.")
        return

    for index, file in enumerate(files, start=1):
        print(f"{index}. {file.relative_to(root)}")
    print("q. Quit")


def display_file(path: Path) -> None:
    """Print the contents of ``path`` with a simple header."""

    print("\n" + "-" * 80)
    print(path)
    print("-" * 80)
    try:
        print(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as exc:  # pragma: no cover - reading error is runtime only
        print(f"Failed to read {path}: {exc}")
    print("-" * 80 + "\n")


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
    files = collect_markdown_files(args.root)

    try:
        while True:
            print_menu(files, args.root)
            if not files:
                return 0

            choice = input("Select a file number to view (or q to quit): ").strip().lower()
            if choice in {"q", "quit", "exit"}:
                return 0
            if not choice.isdigit():
                print("Please enter a valid number or 'q' to quit.")
                continue

            index = int(choice) - 1
            if index < 0 or index >= len(files):
                print("Selection out of range.")
                continue

            display_file(files[index])
            input("Press Enter to return to the list (or Ctrl+C to quit)...")
    except KeyboardInterrupt:
        print("\nExiting Markdown reader.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
