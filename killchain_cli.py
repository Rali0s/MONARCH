"""Interactive CLI teaching the Lockheed Martin Cyber Kill Chain.

This script uses the simple-term-menu library for menu navigation and
ANSI escape codes for simple coloring. It highlights each stage of the
Kill Chain alongside relevant Kali Linux tooling and methodology notes.
"""
import os
from simple_term_menu import TerminalMenu

# ANSI color codes for simple styling.
BOLD = "\033[1m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"

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


def build_menu() -> TerminalMenu:
    """Create the TerminalMenu with styling and title."""
    stages = list(kill_chain_data.keys()) + ["Quit"]
    title = f"{BOLD}{CYAN}KALI-KILLCHAIN EDUCATIONAL MANUAL{RESET}\n"
    return TerminalMenu(stages, title=title, menu_cursor="➤ ", menu_highlight_style=("fg_cyan", "bold"))


def display_stage(stage: str) -> None:
    """Render the selected Kill Chain stage details."""
    info = kill_chain_data[stage]
    clear_screen()
    print(f"{BOLD}{CYAN}{stage}{RESET}\n")
    print(f"{YELLOW}Description:{RESET} {info['description']}\n")
    tools_colored = ", ".join(f"{GREEN}{tool}{RESET}" for tool in info["kali_apps"])
    print(f"{YELLOW}Kali Tools:{RESET} {tools_colored}\n")
    print(f"{YELLOW}Methodology:{RESET} {info['methodology']}\n")
    input("Press Enter to return to menu.")


def run_menu() -> None:
    """Run the interactive menu loop with graceful exit handling."""
    menu = build_menu()
    try:
        while True:
            clear_screen()
            selection_index = menu.show()
            if selection_index is None:
                # User pressed Escape or Ctrl+C inside the menu.
                break
            stages = list(kill_chain_data.keys())
            if selection_index >= len(stages):
                break
            display_stage(stages[selection_index])
    except KeyboardInterrupt:
        pass
    finally:
        clear_screen()
        print("Goodbye! Keep learning and stay safe.")


if __name__ == "__main__":
    run_menu()
