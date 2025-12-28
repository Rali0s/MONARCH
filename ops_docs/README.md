# External Markdown Contracts for MONARCH Ops

This folder is reserved for educational and ethical-hacking Markdown templates pulled from:

- [`tomwechsler/Ethical_Hacking_and_Penetration_Testing`](https://github.com/tomwechsler/Ethical_Hacking_and_Penetration_Testing) → all Markdown documents in the repository
- [`cure53/Contracts`](https://github.com/cure53/Contracts) → all Markdown documents in the repository

Use `scripts/fetch_external_docs.py` to download the source material into the structured subfolders. The script preserves the relative paths from each GitHub archive so the folder layout mirrors the upstream repositories.

> **Note:** If your environment blocks outbound network requests (common on CI runners), the script will log errors while leaving the folder structure intact. Re-run it when network access is available to populate the documents.
