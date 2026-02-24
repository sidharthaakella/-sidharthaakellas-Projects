"""
Life Dashboard — Daily briefing combining weather, tasks, schedule, reminders, and motivation.
Your morning command center.
"""

import random
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich import box

from modules.utils import (
    load_json, now, today_str, time_str, random_quote,
    days_until, friendly_deadline, truncate,
)

console = Console()

# Try to import requests for weather
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

PROFILE_FILE = "profile.json"


# ═══════════════════════════════════════════════════════════════════════════════
#  USER PROFILE
# ═══════════════════════════════════════════════════════════════════════════════

def get_profile() -> dict:
    """Load or create user profile."""
    profile = load_json(PROFILE_FILE, default={})
    return profile


def setup_profile():
    """Interactive profile setup."""
    from rich.prompt import Prompt

    console.print(Panel(
        "[bold cyan]Let's set up your profile![/bold cyan]\n"
        "This helps me personalize your experience.",
        box=box.DOUBLE,
    ))

    profile = get_profile()
    profile["name"] = Prompt.ask("What's your name?", default=profile.get("name", ""))
    profile["nickname"] = Prompt.ask("What should I call you?", default=profile.get("nickname", profile.get("name", "")))
    profile["school"] = Prompt.ask("School/University name", default=profile.get("school", ""))
    profile["major"] = Prompt.ask("Major/Field of study", default=profile.get("major", ""))
    profile["year"] = Prompt.ask("Year (e.g. Freshman, Sophomore)", default=profile.get("year", ""))
    profile["city"] = Prompt.ask("City (for weather)", default=profile.get("city", ""))
    profile["wake_time"] = Prompt.ask("Usual wake-up time", default=profile.get("wake_time", "7:00 AM"))
    profile["sleep_time"] = Prompt.ask("Usual bedtime", default=profile.get("sleep_time", "11:00 PM"))

    from modules.utils import save_json
    save_json(PROFILE_FILE, profile)
    console.print(f"\n[green]✓ Profile saved! Nice to meet you, {profile['nickname']}! 🤝[/green]")
    return profile


# ═══════════════════════════════════════════════════════════════════════════════
#  WEATHER
# ═══════════════════════════════════════════════════════════════════════════════

def get_weather(city: str = "") -> str:
    """Fetch weather using wttr.in (no API key needed)."""
    if not HAS_REQUESTS:
        return "Weather unavailable (install 'requests')"

    if not city:
        profile = get_profile()
        city = profile.get("city", "")

    if not city:
        return "Set your city in profile for weather info"

    try:
        url = f"https://wttr.in/{city}?format=%C+%t+%h+%w"
        response = requests.get(url, timeout=5, headers={"User-Agent": "TwinBot/1.0"})
        if response.status_code == 200:
            return response.text.strip()
        return "Weather data unavailable"
    except Exception:
        return "Could not fetch weather"


def detailed_weather():
    """Show detailed weather forecast."""
    if not HAS_REQUESTS:
        console.print("[red]'requests' not installed.[/red]")
        return

    profile = get_profile()
    city = profile.get("city", "")

    if not city:
        from rich.prompt import Prompt
        city = Prompt.ask("Enter your city")

    console.print(f"[cyan]Fetching weather for {city}...[/cyan]")

    try:
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url, timeout=10, headers={"User-Agent": "TwinBot/1.0"})
        data = response.json()

        current = data.get("current_condition", [{}])[0]
        temp_c = current.get("temp_C", "?")
        temp_f = current.get("temp_F", "?")
        desc = current.get("weatherDesc", [{}])[0].get("value", "Unknown")
        humidity = current.get("humidity", "?")
        wind = current.get("windspeedKmph", "?")
        feels_like = current.get("FeelsLikeC", "?")

        weather_panel = (
            f"  🌡️  Temperature: {temp_c}°C / {temp_f}°F (feels like {feels_like}°C)\n"
            f"  ☁️  Condition: {desc}\n"
            f"  💧 Humidity: {humidity}%\n"
            f"  💨 Wind: {wind} km/h"
        )

        console.print(Panel(
            weather_panel,
            title=f"[bold cyan]🌤️ Weather in {city}[/bold cyan]",
            box=box.ROUNDED,
        ))

        # 3-day forecast
        forecast = data.get("weather", [])
        if forecast:
            table = Table(title="📅 3-Day Forecast", box=box.SIMPLE)
            table.add_column("Date", style="cyan")
            table.add_column("High", style="red")
            table.add_column("Low", style="blue")
            table.add_column("Condition", style="white")

            for day in forecast[:3]:
                date = day.get("date", "?")
                high = day.get("maxtempC", "?")
                low = day.get("mintempC", "?")
                hourly = day.get("hourly", [{}])
                condition = hourly[len(hourly)//2].get("weatherDesc", [{}])[0].get("value", "?") if hourly else "?"
                table.add_row(date, f"{high}°C", f"{low}°C", condition)

            console.print(table)

    except Exception as e:
        console.print(f"[red]Error fetching weather: {e}[/red]")


# ═══════════════════════════════════════════════════════════════════════════════
#  MORNING BRIEFING / DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

def morning_briefing():
    """Display a comprehensive morning briefing dashboard."""
    profile = get_profile()
    name = profile.get("nickname", profile.get("name", "friend"))

    # Greeting based on time of day
    hour = now().hour
    if hour < 12:
        greeting = f"Good morning, {name}! ☀️"
    elif hour < 17:
        greeting = f"Good afternoon, {name}! 🌤️"
    elif hour < 21:
        greeting = f"Good evening, {name}! 🌅"
    else:
        greeting = f"Hey {name}, burning the midnight oil? 🌙"

    # Header
    console.print()
    console.print(Panel(
        f"[bold white]{greeting}[/bold white]\n"
        f"[dim]{today_str()} — {time_str()}[/dim]",
        title="[bold cyan]🤖 TwinBot Daily Briefing[/bold cyan]",
        box=box.DOUBLE,
        padding=(1, 2),
    ))

    # Weather
    weather = get_weather()
    if weather and "unavailable" not in weather.lower() and "set your" not in weather.lower():
        city = profile.get("city", "your area")
        console.print(f"  🌤️  [bold]Weather in {city}:[/bold] {weather}")
    console.print()

    # Today's classes
    schedule = load_json("schedule.json", default=[])
    today = now().strftime("%A")
    todays_classes = [c for c in schedule if c["day"] == today]
    todays_classes.sort(key=lambda c: c["time"])

    if todays_classes:
        console.print("[bold]📚 Today's Classes:[/bold]")
        for c in todays_classes:
            console.print(f"  • {c['time']} — [bold]{c['course']}[/bold] ({c.get('room', 'TBD')})")
    else:
        console.print(f"  📚 No classes today ({today}). Free day! 🎉")
    console.print()

    # Upcoming deadlines
    assignments = load_json("assignments.json", default=[])
    pending_assignments = [a for a in assignments if not a.get("done")]
    pending_assignments.sort(key=lambda a: a["due_date"])
    urgent = [a for a in pending_assignments if days_until(a["due_date"]) <= 3]

    if urgent:
        console.print("[bold red]⚠️ URGENT Deadlines:[/bold red]")
        for a in urgent:
            console.print(f"  🔴 [bold]{a['title']}[/bold] ({a['course']}) — {friendly_deadline(a['due_date'])}")
    elif pending_assignments:
        console.print("[bold]📝 Upcoming Assignments:[/bold]")
        for a in pending_assignments[:3]:
            console.print(f"  • {a['title']} ({a['course']}) — {friendly_deadline(a['due_date'])}")
    else:
        console.print("  📝 No pending assignments. You're all caught up! ✨")
    console.print()

    # Upcoming exams
    exams = load_json("exams.json", default=[])
    upcoming = [e for e in exams if days_until(e["date"]) >= 0]
    upcoming.sort(key=lambda e: e["date"])

    if upcoming:
        console.print("[bold]📖 Upcoming Exams:[/bold]")
        for e in upcoming[:3]:
            d = days_until(e["date"])
            urgency = "[bold red]" if d <= 3 else "[yellow]" if d <= 7 else ""
            end_tag = "[/bold red]" if d <= 3 else "[/yellow]" if d <= 7 else ""
            console.print(f"  • {urgency}{e['title']} ({e['course']}) — {friendly_deadline(e['date'])}{end_tag}")
    console.print()

    # Today's reminders
    reminders = load_json("reminders.json", default=[])
    today_date = now().strftime("%Y-%m-%d")
    todays_reminders = [r for r in reminders if r.get("date") == today_date]

    if todays_reminders:
        console.print("[bold]🔔 Today's Reminders:[/bold]")
        for r in todays_reminders:
            console.print(f"  • {r['text']}")
    console.print()

    # Pending to-dos
    todos = load_json("todos.json", default=[])
    pending_todos = [t for t in todos if not t.get("done")]
    high_priority = [t for t in pending_todos if t.get("priority") == "High"]

    if high_priority:
        console.print("[bold]🔥 High Priority Tasks:[/bold]")
        for t in high_priority[:3]:
            console.print(f"  • {t['task']}")
    elif pending_todos:
        console.print(f"  ✅ You have [bold]{len(pending_todos)}[/bold] pending task(s)")
    console.print()

    # Family events coming up
    events = load_json("family_events.json", default=[])
    upcoming_events = [e for e in events if 0 <= days_until(e.get("date", "1900-01-01")) <= 14]
    if upcoming_events:
        console.print("[bold]👨‍👩‍👧‍👦 Upcoming Family Events:[/bold]")
        for e in upcoming_events:
            console.print(f"  • {e['title']} — {friendly_deadline(e['date'])}")
    console.print()

    # Errands
    errands = load_json("errands.json", default=[])
    pending_errands = [e for e in errands if not e.get("done")]
    if pending_errands:
        console.print(f"  🏃 You have [bold]{len(pending_errands)}[/bold] errand(s) to run")
    console.print()

    # Motivational quote
    console.print(Panel(
        f"[italic]{random_quote()}[/italic]",
        title="[bold green]💡 Quote of the Day[/bold green]",
        box=box.ROUNDED,
    ))


def quick_stats():
    """Show a quick stats summary."""
    profile = get_profile()

    # Gather stats
    schedule = load_json("schedule.json", default=[])
    assignments = load_json("assignments.json", default=[])
    todos = load_json("todos.json", default=[])
    exams = load_json("exams.json", default=[])
    notes = load_json("notes.json", default=[])
    errands = load_json("errands.json", default=[])

    pending_assignments = sum(1 for a in assignments if not a.get("done"))
    done_assignments = sum(1 for a in assignments if a.get("done"))
    pending_todos = sum(1 for t in todos if not t.get("done"))
    done_todos = sum(1 for t in todos if t.get("done"))
    pending_errands = sum(1 for e in errands if not e.get("done"))

    # GPA
    grades = load_json("grades.json", default=[])
    gpa = 0.0
    if grades:
        gpa_scale = {"A+": 4.0, "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7,
                     "C+": 2.3, "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0, "D-": 0.7, "F": 0.0}
        total_pts = sum(gpa_scale.get(g["grade"].upper(), 0) * g["credits"] for g in grades)
        total_creds = sum(g["credits"] for g in grades)
        gpa = total_pts / total_creds if total_creds > 0 else 0

    stats_text = (
        f"  📚 Classes: [bold]{len(schedule)}[/bold]\n"
        f"  📝 Assignments: [bold]{pending_assignments}[/bold] pending / {done_assignments} done\n"
        f"  ✅ To-dos: [bold]{pending_todos}[/bold] pending / {done_todos} done\n"
        f"  📖 Exams: [bold]{len(exams)}[/bold] scheduled\n"
        f"  📓 Notes: [bold]{len(notes)}[/bold] saved\n"
        f"  🏃 Errands: [bold]{pending_errands}[/bold] pending\n"
        f"  🎓 GPA: [bold]{gpa:.2f}[/bold]"
    )

    console.print(Panel(
        stats_text,
        title=f"[bold cyan]📊 Quick Stats — {profile.get('nickname', 'Student')}[/bold cyan]",
        box=box.DOUBLE,
    ))


# ═══════════════════════════════════════════════════════════════════════════════
#  MENU
# ═══════════════════════════════════════════════════════════════════════════════

def dashboard_menu():
    """Interactive dashboard menu."""
    from rich.prompt import Prompt

    actions = {
        "1": ("Morning briefing", morning_briefing),
        "2": ("Quick stats", quick_stats),
        "3": ("Detailed weather", detailed_weather),
        "4": ("Setup / edit profile", setup_profile),
        "0": ("Back to main menu", None),
    }

    while True:
        console.print(Panel("[bold cyan]🏠 Life Dashboard[/bold cyan]", box=box.DOUBLE))
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
