"""Download external Markdown contracts for MONARCH operations.

This script pulls **all Markdown files** from the following sources and stores
them under ``ops_docs/`` while preserving their relative paths:

* ``tomwechsler/Ethical_Hacking_and_Penetration_Testing``
* ``cure53/Contracts``
"""
from __future__ import annotations

import io
import sys
import urllib.request
import zipfile
from pathlib import Path
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parent.parent
DOCS_ROOT = ROOT / "ops_docs"

ARCHIVES = {
    "tomwechsler": "https://github.com/tomwechsler/Ethical_Hacking_and_Penetration_Testing/archive/refs/heads/main.zip",
    "cure53": "https://github.com/cure53/Contracts/archive/refs/heads/master.zip",
}


def ensure_directory(path: Path) -> None:
    """Create a directory if it does not yet exist."""
    path.mkdir(parents=True, exist_ok=True)


def fetch_bytes(url: str) -> bytes:
    """Retrieve raw bytes from a URL."""

    with urllib.request.urlopen(url) as response:
        return response.read()


def extract_markdown_from_archive(
    archive_bytes: bytes, destination_root: Path, drop_parts: int = 1
) -> None:
    """Extract all Markdown files from an archive into ``destination_root``.

    Parameters
    ----------
    archive_bytes:
        Raw bytes of a zip archive.
    destination_root:
        Base directory under which files are written.
    drop_parts:
        Number of path parts to drop from the start of each archive member
        (useful for removing the top-level folder included by GitHub archives).
    """

    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        members = [
            member
            for member in archive.infolist()
            if member.filename.lower().endswith(".md")
        ]
        if not members:
            print("No Markdown files found in archive.")
            return

        for member in members:
            relative_parts: Sequence[str] = Path(member.filename).parts[drop_parts:]
            destination = destination_root / Path(*relative_parts)

            if member.is_dir():
                ensure_directory(destination)
                continue

            ensure_directory(destination.parent)
            print(f"Extracting {destination} ...")
            destination.write_bytes(archive.read(member))


def fetch_repo_markdown(source_key: str, archive_url: str) -> None:
    """Download and extract Markdown files for a given repository archive."""

    destination = DOCS_ROOT / source_key
    ensure_directory(destination)

    print(f"Downloading {source_key} archive ...")
    archive_bytes = fetch_bytes(archive_url)
    extract_markdown_from_archive(archive_bytes, destination)
    print(f"Saved {source_key} Markdown files.")


def main(argv: Iterable[str] | None = None) -> int:
    try:
        for source_key, archive_url in ARCHIVES.items():
            fetch_repo_markdown(source_key, archive_url)
    except Exception as exc:  # pragma: no cover - network failures are runtime concerns
        print(f"Failed to download Markdown files: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
