# MONARCH

Interactive CLI educational manual for the Lockheed Martin Cyber Kill Chain using the Cement framework.

## Setup

Install dependencies (recommend using a virtual environment):

```bash
pip install -r requirements.txt
```

## Usage

```bash
python killchain_cli.py
```

Select a stage by entering its number, view the description, tooling, and methodology, then press Enter to return to the menu. Press
`q` or `Ctrl+C` to exit gracefully.

## External contract references

Run the helper script to pull educational and ethical-hacking Markdown references into `ops_docs/`:

```bash
python scripts/fetch_external_docs.py
```

The script retrieves all Markdown files from the `tomwechsler/Ethical_Hacking_and_Penetration_Testing` repository and all Markdown files from the `cure53/Contracts` repository while preserving their relative paths. If the environment blocks outbound network access, rerun the script when connectivity is available.

## Browse downloaded Markdown files

Use the Markdown reader to sort and view the downloaded ethical-hacking documents:

```bash
python scripts/md_reader.py
```

Pass `--root <path>` to point the reader at an alternate directory if you keep Markdown files outside `ops_docs/`.
