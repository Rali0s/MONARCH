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

kill_chain_data = {
    "Reconnaissance": {
        "description": "Gather information about the target via active scanning and OSINT techniques.",
        "kali_apps": ["Nmap", "theHarvester"],
        "methodology": (
            "Use port scans and service detection to map exposed surfaces, then pair the findings with "
            "public data collection to guide later attacks."
        ),
    },
    "Weaponization": {
        "description": "Prepare malicious payloads and couple them with suitable exploits.",
        "kali_apps": ["msfvenom", "SET"],
        "methodology": (
            "Craft payloads (shellcode, droppers, phishing lures) that align with identified weaknesses, "
            "readying them for delivery."
        ),
    },
    "Delivery": {
        "description": "Transmit the weaponized payload to the target environment.",
        "kali_apps": ["Evilginx2", "Social-Engineer Toolkit"],
        "methodology": (
            "Send phishing messages, host rogue access points, or otherwise transport the payload into the "
            "target's sphere."
        ),
    },
    "Exploitation": {
        "description": "Execute code on the target by leveraging discovered vulnerabilities.",
        "kali_apps": ["Metasploit", "SQLmap"],
        "methodology": (
            "Trigger exploits that run the payload or abuse logic flaws such as SQL injection to gain execution."
        ),
    },
    "Installation": {
        "description": "Establish persistence and install backdoors for ongoing access.",
        "kali_apps": ["Empire", "Netcat"],
        "methodology": (
            "Deploy agents, reverse shells, or service modifications that survive reboots and keep footholds alive."
        ),
    },
    "C2": {
        "description": "Create a command-and-control channel to manage compromised hosts.",
        "kali_apps": ["Sliver", "Pwnat"],
        "methodology": (
            "Open interactive channels, beaconing sessions, or NAT-bypassing tunnels to orchestrate operations."
        ),
    },
    "Actions": {
        "description": "Achieve mission objectives such as data exfiltration or credential theft.",
        "kali_apps": ["PyExfil", "Mimikatz"],
        "methodology": (
            "Collect, stage, and extract target data or secrets, maintaining operational security throughout."
        ),
    },
}


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


def render_stage_table(stages: list[str]) -> str:
    """Render stages as a two-column grid for a compact dash look."""

    col_width = 32
    padded = [f"{BOLD}{str(i+1).rjust(2)}{RESET} {CYAN}{stage}{RESET}" for i, stage in enumerate(stages)]
    # Split into two columns
    left = padded[::2]
    right = padded[1::2]
    # Pad shorter column
    while len(left) > len(right):
        right.append("")
    lines: list[str] = []
    for lval, rval in zip(left, right):
        lines.append(f" {lval.ljust(col_width)}{rval}")
    return "\n".join(lines)


def render_stage(stage: str) -> None:
    """Render the selected Kill Chain stage details."""
    info = kill_chain_data[stage]
    clear_screen()
    print(f"{BOLD}{CYAN}{stage}{RESET}\n")
    print(f"{YELLOW}Description:{RESET} {info['description']}\n")
    tools_colored = ", ".join(f"{GREEN}{tool}{RESET}" for tool in info["kali_apps"])
    print(f"{YELLOW}Kali Tools:{RESET} {tools_colored}\n")
    print(f"{YELLOW}Methodology:{RESET} {info['methodology']}\n")
    input("Press Enter to return to menu.")


class KillChainController(Controller):
    class Meta:
        label = "base"
        help = "KALI-KILLCHAIN EDUCATIONAL MANUAL"

    @ex(help="Launch the interactive Kill Chain tutorial")
    def default(self) -> None:
        stages = list(kill_chain_data.keys())
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
