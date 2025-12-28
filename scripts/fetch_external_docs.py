"""Download external Markdown contracts for MONARCH operations.

This script pulls:
- Contract_Agreement.md from tomwechsler/Ethical_Hacking_and_Penetration_Testing
- All Markdown files from cure53/Contracts via the repository archive

Downloaded files are stored under ops_docs/ with source-based subfolders.
"""
from __future__ import annotations

import io
import sys
import urllib.request
import zipfile
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
DOCS_ROOT = ROOT / "ops_docs"

TOMWECHSLER_URL = (
    "https://raw.githubusercontent.com/"
    "tomwechsler/Ethical_Hacking_and_Penetration_Testing/"
    "main/Penetration_Testing/Contract_Agreement.md"
)
CURE53_ARCHIVE_URL = (
    "https://github.com/cure53/Contracts/archive/refs/heads/master.zip"
)


def ensure_directory(path: Path) -> None:
    """Create a directory if it does not yet exist."""
    path.mkdir(parents=True, exist_ok=True)


def fetch_bytes(url: str) -> bytes:
    """Retrieve raw bytes from a URL."""
    with urllib.request.urlopen(url) as response:
        return response.read()


def save_contract_agreement() -> None:
    destination = DOCS_ROOT / "tomwechsler" / "Contract_Agreement.md"
    ensure_directory(destination.parent)
    print(f"Downloading Contract_Agreement.md to {destination} ...")
    content = fetch_bytes(TOMWECHSLER_URL)
    destination.write_bytes(content)
    print("Saved tomwechsler contract.")


def extract_cure53_contracts() -> None:
    ensure_directory(DOCS_ROOT / "cure53")
    print("Downloading cure53 Contracts archive ...")
    archive_bytes = fetch_bytes(CURE53_ARCHIVE_URL)
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        members = [
            member for member in archive.infolist() if member.filename.lower().endswith(".md")
        ]
        if not members:
            print("No Markdown files found in archive.")
            return
        for member in members:
            relative_path = Path(member.filename).parts[1:]  # drop top-level folder
            destination = DOCS_ROOT / "cure53" / Path(*relative_path)
            if member.is_dir():
                ensure_directory(destination)
                continue
            ensure_directory(destination.parent)
            print(f"Extracting {destination} ...")
            destination.write_bytes(archive.read(member))
    print("Saved cure53 contracts.")


def main(argv: Iterable[str] | None = None) -> int:
    try:
        save_contract_agreement()
    except Exception as exc:  # pragma: no cover - network failures are runtime concerns
        print(f"Failed to download Contract_Agreement.md: {exc}", file=sys.stderr)
    try:
        extract_cure53_contracts()
    except Exception as exc:  # pragma: no cover - network failures are runtime concerns
        print(f"Failed to download cure53 contracts: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
