"""
Personal Secretary — To-do lists, daily planner, notes, reminders, contacts.
"""

from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich import box

from modules.utils import (
    load_json, save_json, generate_id, now, today_str,
    friendly_deadline, days_until, truncate,
)

console = Console()

TODOS_FILE = "todos.json"
NOTES_FILE = "notes.json"
REMINDERS_FILE = "reminders.json"
CONTACTS_FILE = "contacts.json"
PLANNER_FILE = "planner.json"


# ═══════════════════════════════════════════════════════════════════════════════
#  TO-DO LIST
# ═══════════════════════════════════════════════════════════════════════════════

def view_todos():
    """Display all to-do items grouped by priority."""
    todos = load_json(TODOS_FILE, default=[])
    if not todos:
        console.print("[yellow]Your to-do list is empty. Time to add some tasks![/yellow]")
        return

    # Sort: incomplete first, then by priority
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    todos.sort(key=lambda t: (t.get("done", False), priority_order.get(t.get("priority", "Medium"), 1)))

    table = Table(title="✅ To-Do List", box=box.ROUNDED, show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Task", style="bold white", min_width=30)
    table.add_column("Priority", style="red", justify="center")
    table.add_column("Category", style="cyan")
    table.add_column("Due", style="yellow")
    table.add_column("Status", style="green", justify="center")

    for i, t in enumerate(todos, 1):
        status = "✅" if t.get("done") else "⬜"
        due = friendly_deadline(t["due_date"]) if t.get("due_date") else "—"
        style = "dim" if t.get("done") else ""
        table.add_row(
            str(i), t["task"], t.get("priority", "Medium"),
            t.get("category", "General"), due, status, style=style,
        )

    console.print(table)

    done_count = sum(1 for t in todos if t.get("done"))
    total = len(todos)
    console.print(f"  Progress: {done_count}/{total} tasks complete ({done_count/total*100:.0f}%)")


def add_todo():
    """Add a new to-do item."""
    console.print(Panel("[bold cyan]Add New To-Do[/bold cyan]"))
    task = Prompt.ask("What do you need to do?")
    priority = Prompt.ask("Priority", choices=["High", "Medium", "Low"], default="Medium")
    category = Prompt.ask("Category (e.g. School, Personal, Family, Work)", default="General")
    due_date = Prompt.ask("Due date (YYYY-MM-DD, or press Enter to skip)", default="")

    todos = load_json(TODOS_FILE, default=[])
    todos.append({
        "id": generate_id(),
        "task": task,
        "priority": priority,
        "category": category,
        "due_date": due_date if due_date else None,
        "done": False,
        "created": now().isoformat(),
    })
    save_json(TODOS_FILE, todos)
    console.print(f"[green]✓ Added: '{task}' [{priority}][/green]")


def complete_todo():
    """Mark a to-do as done."""
    todos = load_json(TODOS_FILE, default=[])
    pending = [t for t in todos if not t.get("done")]
    if not pending:
        console.print("[green]All tasks complete! You're on fire! 🔥[/green]")
        return

    view_todos()
    idx = IntPrompt.ask("Enter task number to complete") - 1
    if 0 <= idx < len(todos):
        todos[idx]["done"] = True
        todos[idx]["completed_date"] = now().isoformat()
        save_json(TODOS_FILE, todos)
        console.print(f"[green]✓ '{todos[idx]['task']}' marked complete! 🎉[/green]")
    else:
        console.print("[red]Invalid task number.[/red]")


def delete_todo():
    """Delete a to-do item."""
    todos = load_json(TODOS_FILE, default=[])
    if not todos:
        console.print("[yellow]No tasks to delete.[/yellow]")
        return

    view_todos()
    idx = IntPrompt.ask("Enter task number to delete") - 1
    if 0 <= idx < len(todos):
        removed = todos.pop(idx)
        save_json(TODOS_FILE, todos)
        console.print(f"[green]✓ Deleted: '{removed['task']}'[/green]")
    else:
        console.print("[red]Invalid task number.[/red]")


def pending_todos(limit: int = 5) -> list[dict]:
    """Return pending to-dos for dashboard."""
    todos = load_json(TODOS_FILE, default=[])
    pending = [t for t in todos if not t.get("done")]
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    pending.sort(key=lambda t: priority_order.get(t.get("priority", "Medium"), 1))
    return pending[:limit]


# ═══════════════════════════════════════════════════════════════════════════════
#  QUICK NOTES
# ═══════════════════════════════════════════════════════════════════════════════

def view_notes():
    """Display all saved notes."""
    notes = load_json(NOTES_FILE, default=[])
    if not notes:
        console.print("[yellow]No notes saved yet.[/yellow]")
        return

    for i, n in enumerate(notes, 1):
        title = n.get("title", "Untitled")
        created = n.get("created", "Unknown")[:10]
        tag = n.get("tag", "General")
        console.print(Panel(
            f"[white]{n['content']}[/white]",
            title=f"[bold cyan]#{i} {title}[/bold cyan] [dim]({tag} — {created})[/dim]",
            box=box.ROUNDED,
        ))


def add_note():
    """Save a quick note."""
    console.print(Panel("[bold cyan]Quick Note[/bold cyan]"))
    title = Prompt.ask("Title")
    content = Prompt.ask("Note content")
    tag = Prompt.ask("Tag (e.g. Ideas, School, Personal)", default="General")

    notes = load_json(NOTES_FILE, default=[])
    notes.append({
        "id": generate_id(),
        "title": title,
        "content": content,
        "tag": tag,
        "created": now().isoformat(),
    })
    save_json(NOTES_FILE, notes)
    console.print(f"[green]✓ Note saved: '{title}'[/green]")


def search_notes():
    """Search notes by keyword."""
    notes = load_json(NOTES_FILE, default=[])
    if not notes:
        console.print("[yellow]No notes to search.[/yellow]")
        return

    keyword = Prompt.ask("Search keyword").lower()
    results = [n for n in notes if keyword in n.get("title", "").lower() or keyword in n.get("content", "").lower()]

    if not results:
        console.print(f"[yellow]No notes matching '{keyword}'.[/yellow]")
        return

    console.print(f"[green]Found {len(results)} note(s):[/green]")
    for n in results:
        console.print(f"  • [bold]{n['title']}[/bold]: {truncate(n['content'], 60)}")


def delete_note():
    """Delete a note."""
    notes = load_json(NOTES_FILE, default=[])
    if not notes:
        console.print("[yellow]No notes to delete.[/yellow]")
        return

    view_notes()
    idx = IntPrompt.ask("Enter note number to delete") - 1
    if 0 <= idx < len(notes):
        removed = notes.pop(idx)
        save_json(NOTES_FILE, notes)
        console.print(f"[green]✓ Deleted note: '{removed['title']}'[/green]")
    else:
        console.print("[red]Invalid note number.[/red]")


# ═══════════════════════════════════════════════════════════════════════════════
#  REMINDERS
# ═══════════════════════════════════════════════════════════════════════════════

def view_reminders():
    """Display all reminders."""
    reminders = load_json(REMINDERS_FILE, default=[])
    if not reminders:
        console.print("[yellow]No reminders set.[/yellow]")
        return

    reminders.sort(key=lambda r: r.get("date", "9999-99-99"))

    table = Table(title="🔔 Reminders", box=box.ROUNDED, show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Reminder", style="bold white", min_width=30)
    table.add_column("Date", style="yellow")
    table.add_column("When", style="magenta")
    table.add_column("Repeat", style="cyan")

    for i, r in enumerate(reminders, 1):
        when = friendly_deadline(r["date"]) if r.get("date") else "—"
        table.add_row(str(i), r["text"], r.get("date", "—"), when, r.get("repeat", "Once"))

    console.print(table)


def add_reminder():
    """Set a new reminder."""
    console.print(Panel("[bold cyan]Set a Reminder[/bold cyan]"))
    text = Prompt.ask("What should I remind you about?")
    date = Prompt.ask("Date (YYYY-MM-DD)")
    repeat = Prompt.ask("Repeat", choices=["Once", "Daily", "Weekly", "Monthly"], default="Once")

    reminders = load_json(REMINDERS_FILE, default=[])
    reminders.append({
        "id": generate_id(),
        "text": text,
        "date": date,
        "repeat": repeat,
        "created": now().isoformat(),
    })
    save_json(REMINDERS_FILE, reminders)
    console.print(f"[green]✓ Reminder set: '{text}' — {friendly_deadline(date)}[/green]")


def todays_reminders() -> list[dict]:
    """Return reminders due today (for dashboard)."""
    reminders = load_json(REMINDERS_FILE, default=[])
    today = now().strftime("%Y-%m-%d")
    return [r for r in reminders if r.get("date") == today]


def delete_reminder():
    """Delete a reminder."""
    reminders = load_json(REMINDERS_FILE, default=[])
    if not reminders:
        console.print("[yellow]No reminders to delete.[/yellow]")
        return

    view_reminders()
    idx = IntPrompt.ask("Enter reminder number to delete") - 1
    if 0 <= idx < len(reminders):
        removed = reminders.pop(idx)
        save_json(REMINDERS_FILE, reminders)
        console.print(f"[green]✓ Deleted reminder: '{removed['text']}'[/green]")
    else:
        console.print("[red]Invalid reminder number.[/red]")


# ═══════════════════════════════════════════════════════════════════════════════
#  CONTACTS
# ═══════════════════════════════════════════════════════════════════════════════

def view_contacts():
    """Display all contacts."""
    contacts = load_json(CONTACTS_FILE, default=[])
    if not contacts:
        console.print("[yellow]No contacts saved.[/yellow]")
        return

    table = Table(title="📇 Contacts", box=box.ROUNDED, show_lines=True)
    table.add_column("Name", style="bold cyan")
    table.add_column("Phone", style="green")
    table.add_column("Email", style="yellow")
    table.add_column("Relation", style="magenta")
    table.add_column("Notes", style="white")

    for c in contacts:
        table.add_row(
            c["name"], c.get("phone", "—"), c.get("email", "—"),
            c.get("relation", "—"), truncate(c.get("notes", ""), 30),
        )

    console.print(table)


def add_contact():
    """Add a new contact."""
    console.print(Panel("[bold cyan]Add Contact[/bold cyan]"))
    name = Prompt.ask("Name")
    phone = Prompt.ask("Phone number", default="")
    email = Prompt.ask("Email", default="")
    relation = Prompt.ask("Relation (e.g. Friend, Professor, Family)", default="Other")
    notes = Prompt.ask("Notes", default="")

    contacts = load_json(CONTACTS_FILE, default=[])
    contacts.append({
        "id": generate_id(),
        "name": name,
        "phone": phone,
        "email": email,
        "relation": relation,
        "notes": notes,
    })
    save_json(CONTACTS_FILE, contacts)
    console.print(f"[green]✓ Contact '{name}' saved.[/green]")


# ═══════════════════════════════════════════════════════════════════════════════
#  DAILY PLANNER
# ═══════════════════════════════════════════════════════════════════════════════

def view_daily_plan():
    """View today's plan."""
    planner = load_json(PLANNER_FILE, default={})
    today = now().strftime("%Y-%m-%d")
    plan = planner.get(today, [])

    if not plan:
        console.print(f"[yellow]No plan for today ({today_str()}). Let's make one![/yellow]")
        return

    console.print(Panel(f"[bold cyan]📋 Daily Plan — {today_str()}[/bold cyan]", box=box.DOUBLE))
    for i, item in enumerate(plan, 1):
        status = "✅" if item.get("done") else "⬜"
        time_slot = item.get("time", "")
        console.print(f"  {status} [bold]{time_slot}[/bold]  {item['task']}")


def add_to_daily_plan():
    """Add an item to today's plan."""
    planner = load_json(PLANNER_FILE, default={})
    today = now().strftime("%Y-%m-%d")

    time_slot = Prompt.ask("Time (e.g. 09:00 AM)")
    task = Prompt.ask("What's the plan?")

    if today not in planner:
        planner[today] = []

    planner[today].append({
        "time": time_slot,
        "task": task,
        "done": False,
    })

    # Sort by time
    planner[today].sort(key=lambda x: x["time"])
    save_json(PLANNER_FILE, planner)
    console.print(f"[green]✓ Added to today's plan: {time_slot} — {task}[/green]")


def complete_plan_item():
    """Mark a daily plan item as done."""
    planner = load_json(PLANNER_FILE, default={})
    today = now().strftime("%Y-%m-%d")
    plan = planner.get(today, [])

    if not plan:
        console.print("[yellow]No plan items for today.[/yellow]")
        return

    view_daily_plan()
    idx = IntPrompt.ask("Enter item number to complete") - 1
    if 0 <= idx < len(plan):
        plan[idx]["done"] = True
        planner[today] = plan
        save_json(PLANNER_FILE, planner)
        console.print(f"[green]✓ Plan item completed![/green]")
    else:
        console.print("[red]Invalid item number.[/red]")


# ═══════════════════════════════════════════════════════════════════════════════
#  MENU
# ═══════════════════════════════════════════════════════════════════════════════

def secretary_menu():
    """Interactive personal secretary menu."""
    actions = {
        "1": ("View to-do list", view_todos),
        "2": ("Add to-do", add_todo),
        "3": ("Complete to-do", complete_todo),
        "4": ("Delete to-do", delete_todo),
        "5": ("View daily plan", view_daily_plan),
        "6": ("Add to daily plan", add_to_daily_plan),
        "7": ("Complete plan item", complete_plan_item),
        "8": ("View notes", view_notes),
        "9": ("Add a note", add_note),
        "10": ("Search notes", search_notes),
        "11": ("Delete a note", delete_note),
        "12": ("View reminders", view_reminders),
        "13": ("Add reminder", add_reminder),
        "14": ("Delete reminder", delete_reminder),
        "15": ("View contacts", view_contacts),
        "16": ("Add contact", add_contact),
        "0": ("Back to main menu", None),
    }

    while True:
        console.print(Panel("[bold cyan]📋 Personal Secretary[/bold cyan]", box=box.DOUBLE))
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
