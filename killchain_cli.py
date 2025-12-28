"""Interactive CLI teaching the Lockheed Martin Cyber Kill Chain.

This script uses the Cement framework for command routing and ANSI escape
codes for simple coloring. It highlights each stage of the Kill Chain
alongside relevant Kali Linux tooling and methodology notes.
"""
from cement import App, Controller, ex
import os

# ANSI color codes for simple styling.
BOLD = "\033[1m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
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


def format_stage_line(index: int, stage: str) -> str:
    """Return a styled menu line for a stage."""
    return f"{BOLD}{index}. {CYAN}{stage}{RESET}"


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
        try:
            while True:
                clear_screen()
                print(f"{BOLD}{CYAN}KALI-KILLCHAIN EDUCATIONAL MANUAL{RESET}\n")
                for idx, stage in enumerate(stages, start=1):
                    print(format_stage_line(idx, stage))
                print(f"{BOLD}{CYAN}q. Quit{RESET}\n")

                choice = input("Select a stage by number (or q to quit): ").strip().lower()
                if choice in {"q", "quit", "exit"}:
                    break
                if not choice:
                    continue
                if not choice.isdigit():
                    print(f"{RED}Please enter a valid number or 'q' to quit.{RESET}")
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
