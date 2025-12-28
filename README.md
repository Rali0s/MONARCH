# MONARCH

Interactive CLI educational manual for the Lockheed Martin Cyber Kill Chain using the Cement framework, plus an embedded Markdown
browser for the ethical-hacking docs pulled into `ops_docs/`.

## Setup

Install dependencies (recommend using a virtual environment):

```bash
pip install -r requirements.txt
```

## Usage

```bash
python killchain_cli.py
```

The dashboard auto-resizes the terminal to a wide/tall layout where supported. From the main menu you can:

- Enter a stage number to view Kill Chain details.
- Type `d` to enter the Markdown browser for `ops_docs/`.
- Type `q` or press `Ctrl+C` to exit gracefully.

### Markdown browser controls

Within the embedded Markdown reader:

- Enter a number to page through a file (uses `$PAGER` or `less -R` for scrollable output).
- Use `vim <number>` or `nano <number>` to open a document in your preferred editor before returning to the menu.
- Type `b` to go back to the Kill Chain menu or `q` to quit entirely.

## External contract references

Run the helper script to pull educational and ethical-hacking Markdown references into `ops_docs/`:

```bash
python scripts/fetch_external_docs.py
```

The script retrieves all Markdown files from the `tomwechsler/Ethical_Hacking_and_Penetration_Testing` repository and all Markdown files from the `cure53/Contracts` repository while preserving their relative paths. If the environment blocks outbound network access, rerun the script when connectivity is available.

## Browse downloaded Markdown files

Use the Markdown reader to sort and view the downloaded ethical-hacking documents from outside the dashboard as well:

```bash
python scripts/md_reader.py
```

Pass `--root <path>` to point the reader at an alternate directory if you keep Markdown files outside `ops_docs/`.
