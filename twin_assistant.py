#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ████████╗██╗    ██╗██╗███╗   ██╗██████╗  ██████╗ ████████╗                ║
║   ╚══██╔══╝██║    ██║██║████╗  ██║██╔══██╗██╔═══██╗╚══██╔══╝                ║
║      ██║   ██║ █╗ ██║██║██╔██╗ ██║██████╔╝██║   ██║   ██║                   ║
║      ██║   ██║███╗██║██║██║╚██╗██║██╔══██╗██║   ██║   ██║                   ║
║      ██║   ╚███╔███╔╝██║██║ ╚████║██████╔╝╚██████╔╝   ██║                   ║
║      ╚═╝    ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝╚═════╝  ╚═════╝    ╚═╝                   ║
║                                                                              ║
║   Your Digital Twin — Student Life Manager & Personal Secretary              ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

TwinBot is your AI-powered personal assistant that manages your life as a
student and a son. It handles scheduling, assignments, research, family duties,
and acts as your digital twin for everyday tasks.

Usage:
    python twin_assistant.py

Author: Built with love for students everywhere.
"""

import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich import box

from modules.utils import load_json, save_json, today_str, time_str, random_quote
from modules.life_dashboard import morning_briefing, get_profile, setup_profile
from modules.student_manager import student_menu
from modules.personal_secretary import secretary_menu
from modules.internet_researcher import researcher_menu
from modules.family_helper import family_menu
from modules.study_analyzer import study_analyzer_menu
from modules.life_dashboard import dashboard_menu

console = Console()

# ─── ASCII Art Banner ────────────────────────────────────────────────────────

BANNER = """
[bold cyan]
  ████████╗██╗    ██╗██╗███╗   ██╗██████╗  ██████╗ ████████╗
  ╚══██╔══╝██║    ██║██║████╗  ██║██╔══██╗██╔═══██╗╚══██╔══╝
     ██║   ██║ █╗ ██║██║██╔██╗ ██║██████╔╝██║   ██║   ██║
     ██║   ██║███╗██║██║██║╚██╗██║██╔══██╗██║   ██║   ██║
     ██║   ╚███╔███╔╝██║██║ ╚████║██████╔╝╚██████╔╝   ██║
     ╚═╝    ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝╚═════╝  ╚═════╝    ╚═╝
[/bold cyan]
[dim]  Your Digital Twin — Student Life Manager & Personal Secretary[/dim]
"""


def show_banner():
    """Display the TwinBot banner."""
    console.print(BANNER)


def first_time_setup():
    """Check if this is the first run and do initial setup."""
    profile = get_profile()
    if not profile.get("name"):
        console.print(Panel(
            "[bold white]Welcome to TwinBot! 🤖[/bold white]\n\n"
            "I'm your digital twin — here to manage your student life,\n"
            "handle research, keep track of family duties, and be your\n"
            "personal secretary. Let's get you set up!",
            title="[bold cyan]First Time Setup[/bold cyan]",
            box=box.DOUBLE,
            padding=(1, 2),
        ))
        return setup_profile()
    return profile


def main_menu():
    """Display and handle the main menu."""
    profile = first_time_setup()
    name = profile.get("nickname", profile.get("name", "friend"))

    # Show morning briefing on startup
    show_banner()
    console.print(f"  [bold green]Hey {name}! Ready to crush it today.[/bold green]")
    console.print(f"  [dim]{today_str()} — {time_str()}[/dim]\n")

    # Quick motivational quote
    console.print(f"  [italic dim]\"{random_quote()}\"[/italic dim]\n")

    # Main loop
    while True:
        console.print(Panel(
            "[bold white]What would you like to do?[/bold white]",
            title="[bold cyan]🤖 TwinBot — Main Menu[/bold cyan]",
            box=box.DOUBLE,
        ))

        menu_items = [
            ("1", "🏠 Life Dashboard", "Morning briefing, weather, quick stats"),
            ("2", "🎓 Student Manager", "Classes, assignments, GPA, exams, study timer"),
            ("3", "📋 Personal Secretary", "To-dos, planner, notes, reminders, contacts"),
            ("4", "🌐 Internet Researcher", "Wikipedia, news, web reader, fact lookup"),
            ("5", "👨‍👩‍👧‍👦 Family Helper", "Family events, errands, gift ideas"),
            ("6", "📊 Study Analyzer", "Analyze study habits, get recommendations"),
            ("7", "⚡ Quick Actions", "Fast access to common tasks"),
            ("0", "👋 Exit", "See you later!"),
        ]

        for key, title, desc in menu_items:
            console.print(f"  [bold cyan]{key}[/bold cyan]  [bold]{title}[/bold]  [dim]— {desc}[/dim]")

        console.print()
        choice = Prompt.ask("Choose an option", default="0")

        if choice == "0":
            console.print(f"\n[bold green]See you later, {name}! Keep being awesome! 🚀[/bold green]")
            console.print("[dim]Remember: You've got this. 💪[/dim]\n")
            break
        elif choice == "1":
            dashboard_menu()
        elif choice == "2":
            student_menu()
        elif choice == "3":
            secretary_menu()
        elif choice == "4":
            researcher_menu()
        elif choice == "5":
            family_menu()
        elif choice == "6":
            study_analyzer_menu()
        elif choice == "7":
            quick_actions_menu()
        else:
            console.print("[red]Invalid choice. Try again.[/red]")


def quick_actions_menu():
    """Quick access to the most common tasks."""
    actions = {
        "1": ("Add a to-do", _quick_add_todo),
        "2": ("Add a quick note", _quick_add_note),
        "3": ("View today's schedule", _quick_today),
        "4": ("Quick fact lookup", _quick_fact),
        "5": ("Morning briefing", morning_briefing),
        "0": ("Back to main menu", None),
    }

    while True:
        console.print(Panel("[bold cyan]⚡ Quick Actions[/bold cyan]", box=box.DOUBLE))
        for key, (label, _) in actions.items():
            console.print(f"  [bold cyan]{key}[/bold cyan]  {label}")

        choice = Prompt.ask("\nChoose an option", default="0")
        if choice == "0":
            break
        action = actions.get(choice)
        if action:
            _, func = action
            if func:
                console.print()
                func()
                console.print()
        else:
            console.print("[red]Invalid choice.[/red]")


def _quick_add_todo():
    """Quickly add a to-do without going through the full menu."""
    from modules.personal_secretary import add_todo
    add_todo()


def _quick_add_note():
    """Quickly add a note."""
    from modules.personal_secretary import add_note
    add_note()


def _quick_today():
    """Show today's classes."""
    from modules.student_manager import todays_classes
    todays_classes()


def _quick_fact():
    """Quick fact lookup."""
    from modules.internet_researcher import quick_fact_lookup
    quick_fact_lookup()


# ═══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        console.print("\n\n[bold yellow]Interrupted. See you next time! 👋[/bold yellow]\n")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]Unexpected error: {e}[/bold red]")
        console.print("[dim]Please report this issue.[/dim]")
        sys.exit(1)
