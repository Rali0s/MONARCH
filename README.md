# MONARCH

Interactive CLI educational manual for the Lockheed Martin Cyber Kill Chain using `simple-term-menu`.

## Setup

Install dependencies (recommend using a virtual environment):

```bash
pip install -r requirements.txt
```

## Usage

```bash
python killchain_cli.py
```

Use the arrow keys to select a stage of the Kill Chain and press Enter to read its description, tooling, and methodology. Press
`Ctrl+C` or choose **Quit** to exit gracefully.

## External contract references

Run the helper script to pull educational and ethical-hacking contract templates into `ops_docs/`:

```bash
python scripts/fetch_external_docs.py
```

The script retrieves `Contract_Agreement.md` from the `tomwechsler/Ethical_Hacking_and_Penetration_Testing` repository and all Markdown files from the `cure53/Contracts` repository. If the environment blocks outbound network access, rerun the script when connectivity is available.
