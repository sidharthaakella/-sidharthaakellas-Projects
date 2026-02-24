"""
Student Manager — Class schedule, assignments, GPA tracker, exam countdown, Pomodoro timer.
"""

import time
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, FloatPrompt, Confirm
from rich import box

from modules.utils import (
    load_json, save_json, generate_id, now, days_until,
    friendly_deadline, today_str,
)

console = Console()

SCHEDULE_FILE = "schedule.json"
ASSIGNMENTS_FILE = "assignments.json"
GRADES_FILE = "grades.json"
EXAMS_FILE = "exams.json"

# ─── Grade scale ─────────────────────────────────────────────────────────────
GPA_SCALE = {
    "A+": 4.0, "A": 4.0, "A-": 3.7,
    "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7,
    "D+": 1.3, "D": 1.0, "D-": 0.7,
    "F": 0.0,
}


# ═══════════════════════════════════════════════════════════════════════════════
#  CLASS SCHEDULE
# ═══════════════════════════════════════════════════════════════════════════════

def view_schedule():
    """Display the weekly class schedule."""
    schedule = load_json(SCHEDULE_FILE, default=[])
    if not schedule:
        console.print("[yellow]No classes in your schedule yet. Add some![/yellow]")
        return

    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    schedule.sort(key=lambda c: (days_order.index(c["day"]) if c["day"] in days_order else 99, c["time"]))

    table = Table(title="📚 Weekly Class Schedule", box=box.ROUNDED, show_lines=True)
    table.add_column("Day", style="bold cyan", min_width=12)
    table.add_column("Time", style="green")
    table.add_column("Course", style="bold white")
    table.add_column("Room", style="magenta")
    table.add_column("Professor", style="yellow")

    for c in schedule:
        table.add_row(c["day"], c["time"], c["course"], c.get("room", "—"), c.get("professor", "—"))

    console.print(table)


def add_class():
    """Add a class to the weekly schedule."""
    console.print(Panel("[bold cyan]Add a New Class[/bold cyan]"))
    course = Prompt.ask("Course name")
    day = Prompt.ask("Day of the week", choices=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    time_slot = Prompt.ask("Time (e.g. 09:00 AM)")
    room = Prompt.ask("Room / Location", default="TBD")
    professor = Prompt.ask("Professor name", default="TBD")

    schedule = load_json(SCHEDULE_FILE, default=[])
    schedule.append({
        "id": generate_id(),
        "course": course,
        "day": day,
        "time": time_slot,
        "room": room,
        "professor": professor,
    })
    save_json(SCHEDULE_FILE, schedule)
    console.print(f"[green]✓ Added [bold]{course}[/bold] on {day} at {time_slot}[/green]")


def remove_class():
    """Remove a class from the schedule."""
    schedule = load_json(SCHEDULE_FILE, default=[])
    if not schedule:
        console.print("[yellow]No classes to remove.[/yellow]")
        return

    view_schedule()
    course = Prompt.ask("Enter the course name to remove")
    new_schedule = [c for c in schedule if c["course"].lower() != course.lower()]
    if len(new_schedule) == len(schedule):
        console.print("[red]Course not found.[/red]")
    else:
        save_json(SCHEDULE_FILE, new_schedule)
        console.print(f"[green]✓ Removed {course} from schedule.[/green]")


def todays_classes():
    """Show only today's classes."""
    schedule = load_json(SCHEDULE_FILE, default=[])
    today = now().strftime("%A")
    todays = [c for c in schedule if c["day"] == today]

    if not todays:
        console.print(f"[green]No classes today ({today}). Enjoy your free time! 🎉[/green]")
        return

    todays.sort(key=lambda c: c["time"])
    table = Table(title=f"📅 Today's Classes — {today}", box=box.ROUNDED)
    table.add_column("Time", style="green")
    table.add_column("Course", style="bold white")
    table.add_column("Room", style="magenta")

    for c in todays:
        table.add_row(c["time"], c["course"], c.get("room", "—"))

    console.print(table)


# ═══════════════════════════════════════════════════════════════════════════════
#  ASSIGNMENTS
# ═══════════════════════════════════════════════════════════════════════════════

def view_assignments():
    """Display all assignments sorted by due date."""
    assignments = load_json(ASSIGNMENTS_FILE, default=[])
    if not assignments:
        console.print("[yellow]No assignments tracked yet.[/yellow]")
        return

    # Sort: incomplete first, then by due date
    assignments.sort(key=lambda a: (a.get("done", False), a["due_date"]))

    table = Table(title="📝 Assignments", box=box.ROUNDED, show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Course", style="cyan")
    table.add_column("Assignment", style="bold white")
    table.add_column("Due Date", style="yellow")
    table.add_column("Deadline", style="magenta")
    table.add_column("Priority", style="red")
    table.add_column("Status", style="green")

    for i, a in enumerate(assignments, 1):
        status = "✅ Done" if a.get("done") else "⏳ Pending"
        deadline = friendly_deadline(a["due_date"])
        priority = a.get("priority", "Medium")
        style = "dim" if a.get("done") else ""
        table.add_row(
            str(i), a["course"], a["title"], a["due_date"],
            deadline, priority, status, style=style,
        )

    console.print(table)


def add_assignment():
    """Add a new assignment."""
    console.print(Panel("[bold cyan]Add New Assignment[/bold cyan]"))
    course = Prompt.ask("Course name")
    title = Prompt.ask("Assignment title")
    due_date = Prompt.ask("Due date (YYYY-MM-DD)")
    priority = Prompt.ask("Priority", choices=["High", "Medium", "Low"], default="Medium")
    notes = Prompt.ask("Notes (optional)", default="")

    assignments = load_json(ASSIGNMENTS_FILE, default=[])
    assignments.append({
        "id": generate_id(),
        "course": course,
        "title": title,
        "due_date": due_date,
        "priority": priority,
        "notes": notes,
        "done": False,
        "created": now().isoformat(),
    })
    save_json(ASSIGNMENTS_FILE, assignments)
    console.print(f"[green]✓ Assignment '[bold]{title}[/bold]' added — due {friendly_deadline(due_date)}[/green]")


def complete_assignment():
    """Mark an assignment as done."""
    assignments = load_json(ASSIGNMENTS_FILE, default=[])
    pending = [a for a in assignments if not a.get("done")]
    if not pending:
        console.print("[green]All assignments are complete! 🎉[/green]")
        return

    view_assignments()
    title = Prompt.ask("Enter assignment title to mark complete")
    for a in assignments:
        if a["title"].lower() == title.lower() and not a.get("done"):
            a["done"] = True
            a["completed_date"] = now().isoformat()
            save_json(ASSIGNMENTS_FILE, assignments)
            console.print(f"[green]✓ '{title}' marked as complete! Great job! 🎉[/green]")
            return
    console.print("[red]Assignment not found or already complete.[/red]")


def upcoming_deadlines(limit: int = 5) -> list[dict]:
    """Return the next *limit* upcoming assignment deadlines (for dashboard)."""
    assignments = load_json(ASSIGNMENTS_FILE, default=[])
    pending = [a for a in assignments if not a.get("done")]
    pending.sort(key=lambda a: a["due_date"])
    return pending[:limit]


# ═══════════════════════════════════════════════════════════════════════════════
#  GPA TRACKER
# ═══════════════════════════════════════════════════════════════════════════════

def view_grades():
    """Display all grades and calculated GPA."""
    grades = load_json(GRADES_FILE, default=[])
    if not grades:
        console.print("[yellow]No grades recorded yet.[/yellow]")
        return

    table = Table(title="🎓 Grade Book", box=box.ROUNDED, show_lines=True)
    table.add_column("Course", style="cyan")
    table.add_column("Credits", style="green", justify="center")
    table.add_column("Grade", style="bold yellow", justify="center")
    table.add_column("Points", style="magenta", justify="center")

    total_points = 0.0
    total_credits = 0

    for g in grades:
        letter = g["grade"].upper()
        credits = g["credits"]
        points = GPA_SCALE.get(letter, 0.0)
        weighted = points * credits
        total_points += weighted
        total_credits += credits
        table.add_row(g["course"], str(credits), letter, f"{points:.1f}")

    console.print(table)

    if total_credits > 0:
        gpa = total_points / total_credits
        color = "green" if gpa >= 3.0 else "yellow" if gpa >= 2.0 else "red"
        console.print(Panel(
            f"[bold {color}]Cumulative GPA: {gpa:.2f}[/bold {color}]  |  "
            f"Total Credits: {total_credits}",
            title="📊 GPA Summary",
        ))
    return grades


def add_grade():
    """Record a grade for a course."""
    console.print(Panel("[bold cyan]Record a Grade[/bold cyan]"))
    course = Prompt.ask("Course name")
    grade = Prompt.ask("Letter grade (e.g. A, B+, C-)")
    credits = IntPrompt.ask("Credit hours", default=3)

    grades = load_json(GRADES_FILE, default=[])
    grades.append({
        "id": generate_id(),
        "course": course,
        "grade": grade.upper(),
        "credits": credits,
        "recorded": now().isoformat(),
    })
    save_json(GRADES_FILE, grades)
    console.print(f"[green]✓ Recorded {grade.upper()} for {course} ({credits} credits)[/green]")


def calculate_gpa() -> float:
    """Calculate and return current GPA (for dashboard)."""
    grades = load_json(GRADES_FILE, default=[])
    if not grades:
        return 0.0
    total_points = sum(GPA_SCALE.get(g["grade"].upper(), 0) * g["credits"] for g in grades)
    total_credits = sum(g["credits"] for g in grades)
    return total_points / total_credits if total_credits > 0 else 0.0


# ═══════════════════════════════════════════════════════════════════════════════
#  EXAM COUNTDOWN
# ═══════════════════════════════════════════════════════════════════════════════

def view_exams():
    """Display upcoming exams with countdown."""
    exams = load_json(EXAMS_FILE, default=[])
    if not exams:
        console.print("[yellow]No exams scheduled.[/yellow]")
        return

    exams.sort(key=lambda e: e["date"])

    table = Table(title="📖 Exam Countdown", box=box.ROUNDED, show_lines=True)
    table.add_column("Course", style="cyan")
    table.add_column("Exam", style="bold white")
    table.add_column("Date", style="yellow")
    table.add_column("Countdown", style="magenta")
    table.add_column("Location", style="green")

    for e in exams:
        d = days_until(e["date"])
        if d < 0:
            countdown = "[dim]Passed[/dim]"
        elif d == 0:
            countdown = "[bold red]TODAY![/bold red]"
        elif d <= 3:
            countdown = f"[bold red]{d} day{'s' if d != 1 else ''} away![/bold red]"
        elif d <= 7:
            countdown = f"[yellow]{d} days away[/yellow]"
        else:
            countdown = f"{d} days away"

        table.add_row(e["course"], e["title"], e["date"], countdown, e.get("location", "—"))

    console.print(table)


def add_exam():
    """Schedule an exam."""
    console.print(Panel("[bold cyan]Schedule an Exam[/bold cyan]"))
    course = Prompt.ask("Course name")
    title = Prompt.ask("Exam title (e.g. Midterm, Final)")
    date = Prompt.ask("Exam date (YYYY-MM-DD)")
    location = Prompt.ask("Location", default="TBD")
    notes = Prompt.ask("Study notes / topics", default="")

    exams = load_json(EXAMS_FILE, default=[])
    exams.append({
        "id": generate_id(),
        "course": course,
        "title": title,
        "date": date,
        "location": location,
        "notes": notes,
    })
    save_json(EXAMS_FILE, exams)
    console.print(f"[green]✓ Exam '{title}' for {course} scheduled on {date} — {friendly_deadline(date)}[/green]")


def upcoming_exams(limit: int = 3) -> list[dict]:
    """Return next upcoming exams (for dashboard)."""
    exams = load_json(EXAMS_FILE, default=[])
    future = [e for e in exams if days_until(e["date"]) >= 0]
    future.sort(key=lambda e: e["date"])
    return future[:limit]


# ═══════════════════════════════════════════════════════════════════════════════
#  POMODORO STUDY TIMER
# ═══════════════════════════════════════════════════════════════════════════════

def pomodoro_timer():
    """Run a Pomodoro study session (25 min work / 5 min break)."""
    console.print(Panel(
        "[bold cyan]🍅 Pomodoro Study Timer[/bold cyan]\n"
        "25 minutes of focused study → 5 minute break\n"
        "Press Ctrl+C to stop early.",
        box=box.DOUBLE,
    ))

    work_minutes = IntPrompt.ask("Work duration (minutes)", default=25)
    break_minutes = IntPrompt.ask("Break duration (minutes)", default=5)
    sessions = IntPrompt.ask("Number of sessions", default=4)

    for session in range(1, sessions + 1):
        console.print(f"\n[bold green]▶ Session {session}/{sessions} — STUDY TIME ({work_minutes} min)[/bold green]")
        try:
            _countdown(work_minutes * 60)
        except KeyboardInterrupt:
            console.print("\n[yellow]Timer stopped.[/yellow]")
            return

        if session < sessions:
            console.print(f"\n[bold cyan]☕ Break time! ({break_minutes} min)[/bold cyan]")
            try:
                _countdown(break_minutes * 60)
            except KeyboardInterrupt:
                console.print("\n[yellow]Break skipped.[/yellow]")

    console.print("\n[bold green]🎉 All sessions complete! Great work![/bold green]")


def _countdown(seconds: int):
    """Display a live countdown timer."""
    for remaining in range(seconds, 0, -1):
        mins, secs = divmod(remaining, 60)
        console.print(f"  ⏱  {mins:02d}:{secs:02d} remaining", end="\r")
        time.sleep(1)
    console.print("  ⏱  00:00 — Time's up! 🔔          ")


# ═══════════════════════════════════════════════════════════════════════════════
#  MENU
# ═══════════════════════════════════════════════════════════════════════════════

def student_menu():
    """Interactive student manager menu."""
    actions = {
        "1": ("View weekly schedule", view_schedule),
        "2": ("Add a class", add_class),
        "3": ("Remove a class", remove_class),
        "4": ("Today's classes", todays_classes),
        "5": ("View assignments", view_assignments),
        "6": ("Add assignment", add_assignment),
        "7": ("Complete assignment", complete_assignment),
        "8": ("View grades & GPA", view_grades),
        "9": ("Add a grade", add_grade),
        "10": ("View exam countdown", view_exams),
        "11": ("Schedule an exam", add_exam),
        "12": ("Pomodoro study timer", pomodoro_timer),
        "0": ("Back to main menu", None),
    }

    while True:
        console.print(Panel("[bold cyan]🎓 Student Manager[/bold cyan]", box=box.DOUBLE))
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
