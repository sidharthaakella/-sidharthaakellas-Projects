"""
Family Helper — Birthday/event tracker, gift ideas, family contact manager, errand list.
Helps you be a great son and family member.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich import box

from modules.utils import (
    load_json, save_json, generate_id, now, days_until,
    friendly_deadline, truncate,
)

console = Console()

FAMILY_FILE = "family.json"
EVENTS_FILE = "family_events.json"
ERRANDS_FILE = "errands.json"
GIFTS_FILE = "gift_ideas.json"


# ═══════════════════════════════════════════════════════════════════════════════
#  FAMILY CONTACTS
# ═══════════════════════════════════════════════════════════════════════════════

def view_family():
    """Display family members."""
    family = load_json(FAMILY_FILE, default=[])
    if not family:
        console.print("[yellow]No family members added yet.[/yellow]")
        return

    table = Table(title="👨‍👩‍👧‍👦 Family Members", box=box.ROUNDED, show_lines=True)
    table.add_column("Name", style="bold cyan")
    table.add_column("Relation", style="magenta")
    table.add_column("Birthday", style="yellow")
    table.add_column("Next Birthday", style="green")
    table.add_column("Phone", style="white")
    table.add_column("Notes", style="dim")

    for m in family:
        bday = m.get("birthday", "")
        next_bday = ""
        if bday:
            # Calculate next birthday
            try:
                this_year = now().year
                bday_this_year = f"{this_year}-{bday[5:]}"
                d = days_until(bday_this_year)
                if d < 0:
                    bday_next_year = f"{this_year + 1}-{bday[5:]}"
                    d = days_until(bday_next_year)
                if d == 0:
                    next_bday = "[bold red]TODAY! 🎂[/bold red]"
                elif d <= 7:
                    next_bday = f"[bold yellow]{d} days! 🎂[/bold yellow]"
                elif d <= 30:
                    next_bday = f"[yellow]{d} days[/yellow]"
                else:
                    next_bday = f"{d} days"
            except (ValueError, IndexError):
                next_bday = "—"

        table.add_row(
            m["name"], m.get("relation", "—"), bday or "—",
            next_bday, m.get("phone", "—"), truncate(m.get("notes", ""), 25),
        )

    console.print(table)


def add_family_member():
    """Add a family member."""
    console.print(Panel("[bold cyan]Add Family Member[/bold cyan]"))
    name = Prompt.ask("Name")
    relation = Prompt.ask("Relation (e.g. Mom, Dad, Sister, Brother, Grandma)")
    birthday = Prompt.ask("Birthday (YYYY-MM-DD)", default="")
    phone = Prompt.ask("Phone number", default="")
    notes = Prompt.ask("Notes (e.g. favorite things, allergies)", default="")

    family = load_json(FAMILY_FILE, default=[])
    family.append({
        "id": generate_id(),
        "name": name,
        "relation": relation,
        "birthday": birthday,
        "phone": phone,
        "notes": notes,
    })
    save_json(FAMILY_FILE, family)
    console.print(f"[green]✓ Added {name} ({relation}) to family.[/green]")


# ═══════════════════════════════════════════════════════════════════════════════
#  FAMILY EVENTS
# ═══════════════════════════════════════════════════════════════════════════════

def view_events():
    """Display upcoming family events."""
    events = load_json(EVENTS_FILE, default=[])
    if not events:
        console.print("[yellow]No family events scheduled.[/yellow]")
        return

    events.sort(key=lambda e: e.get("date", "9999-99-99"))

    table = Table(title="🎉 Family Events", box=box.ROUNDED, show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Event", style="bold white")
    table.add_column("Date", style="yellow")
    table.add_column("Countdown", style="magenta")
    table.add_column("Location", style="cyan")
    table.add_column("Notes", style="dim")

    for i, e in enumerate(events, 1):
        countdown = friendly_deadline(e["date"]) if e.get("date") else "—"
        table.add_row(
            str(i), e["title"], e.get("date", "—"),
            countdown, e.get("location", "—"), truncate(e.get("notes", ""), 30),
        )

    console.print(table)


def add_event():
    """Schedule a family event."""
    console.print(Panel("[bold cyan]Add Family Event[/bold cyan]"))
    title = Prompt.ask("Event name (e.g. Mom's Birthday, Family Dinner)")
    date = Prompt.ask("Date (YYYY-MM-DD)")
    location = Prompt.ask("Location", default="Home")
    notes = Prompt.ask("Notes", default="")

    events = load_json(EVENTS_FILE, default=[])
    events.append({
        "id": generate_id(),
        "title": title,
        "date": date,
        "location": location,
        "notes": notes,
    })
    save_json(EVENTS_FILE, events)
    console.print(f"[green]✓ Event '{title}' scheduled — {friendly_deadline(date)}[/green]")


def upcoming_family_events(limit: int = 3) -> list[dict]:
    """Return upcoming family events (for dashboard)."""
    events = load_json(EVENTS_FILE, default=[])
    future = [e for e in events if days_until(e.get("date", "1900-01-01")) >= 0]
    future.sort(key=lambda e: e["date"])
    return future[:limit]


# ═══════════════════════════════════════════════════════════════════════════════
#  ERRANDS
# ═══════════════════════════════════════════════════════════════════════════════

def view_errands():
    """Display family errands."""
    errands = load_json(ERRANDS_FILE, default=[])
    if not errands:
        console.print("[yellow]No errands to run. Enjoy your free time![/yellow]")
        return

    table = Table(title="🏃 Errands", box=box.ROUNDED, show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Errand", style="bold white", min_width=30)
    table.add_column("For", style="cyan")
    table.add_column("Priority", style="red")
    table.add_column("Status", style="green", justify="center")

    for i, e in enumerate(errands, 1):
        status = "✅" if e.get("done") else "⬜"
        style = "dim" if e.get("done") else ""
        table.add_row(
            str(i), e["task"], e.get("for_whom", "Family"),
            e.get("priority", "Medium"), status, style=style,
        )

    console.print(table)


def add_errand():
    """Add a family errand."""
    console.print(Panel("[bold cyan]Add Errand[/bold cyan]"))
    task = Prompt.ask("What errand do you need to run?")
    for_whom = Prompt.ask("For whom? (e.g. Mom, Dad, Family)", default="Family")
    priority = Prompt.ask("Priority", choices=["High", "Medium", "Low"], default="Medium")

    errands = load_json(ERRANDS_FILE, default=[])
    errands.append({
        "id": generate_id(),
        "task": task,
        "for_whom": for_whom,
        "priority": priority,
        "done": False,
    })
    save_json(ERRANDS_FILE, errands)
    console.print(f"[green]✓ Errand added: '{task}' for {for_whom}[/green]")


def complete_errand():
    """Mark an errand as done."""
    errands = load_json(ERRANDS_FILE, default=[])
    pending = [e for e in errands if not e.get("done")]
    if not pending:
        console.print("[green]All errands done! You're a great family member! 🌟[/green]")
        return

    view_errands()
    idx = IntPrompt.ask("Enter errand number to complete") - 1
    if 0 <= idx < len(errands):
        errands[idx]["done"] = True
        save_json(ERRANDS_FILE, errands)
        console.print(f"[green]✓ Errand completed! 🎉[/green]")
    else:
        console.print("[red]Invalid errand number.[/red]")


# ═══════════════════════════════════════════════════════════════════════════════
#  GIFT IDEAS
# ═══════════════════════════════════════════════════════════════════════════════

def view_gift_ideas():
    """Display saved gift ideas."""
    gifts = load_json(GIFTS_FILE, default=[])
    if not gifts:
        console.print("[yellow]No gift ideas saved yet.[/yellow]")
        return

    table = Table(title="🎁 Gift Ideas", box=box.ROUNDED, show_lines=True)
    table.add_column("For", style="bold cyan")
    table.add_column("Idea", style="white")
    table.add_column("Budget", style="green")
    table.add_column("Occasion", style="yellow")
    table.add_column("Purchased?", style="magenta", justify="center")

    for g in gifts:
        purchased = "✅" if g.get("purchased") else "⬜"
        table.add_row(
            g["for_whom"], g["idea"], g.get("budget", "—"),
            g.get("occasion", "—"), purchased,
        )

    console.print(table)


def add_gift_idea():
    """Save a gift idea."""
    console.print(Panel("[bold cyan]Save Gift Idea[/bold cyan]"))
    for_whom = Prompt.ask("For whom?")
    idea = Prompt.ask("Gift idea")
    budget = Prompt.ask("Budget range (e.g. $20-50)", default="")
    occasion = Prompt.ask("Occasion (e.g. Birthday, Christmas)", default="")

    gifts = load_json(GIFTS_FILE, default=[])
    gifts.append({
        "id": generate_id(),
        "for_whom": for_whom,
        "idea": idea,
        "budget": budget,
        "occasion": occasion,
        "purchased": False,
    })
    save_json(GIFTS_FILE, gifts)
    console.print(f"[green]✓ Gift idea saved: '{idea}' for {for_whom}[/green]")


def generate_gift_suggestions():
    """Generate gift suggestions based on family member info."""
    family = load_json(FAMILY_FILE, default=[])
    if not family:
        console.print("[yellow]Add family members first to get personalized suggestions.[/yellow]")
        return

    console.print(Panel("[bold cyan]🎁 Gift Suggestion Generator[/bold cyan]", box=box.DOUBLE))

    # Generic gift ideas by relation
    suggestions = {
        "Mom": [
            "Spa day gift card", "Personalized photo album", "Scented candles set",
            "Cooking class experience", "Jewelry (necklace/bracelet)", "Indoor plant/succulent",
            "Cozy blanket & book set", "Handwritten letter + flowers",
        ],
        "Dad": [
            "Tech gadget (wireless earbuds, smart watch)", "BBQ/grilling accessories",
            "Sports memorabilia", "Personalized wallet", "Experience gift (concert, game tickets)",
            "Quality coffee/tea set", "Tool set or workshop gear", "Book by his favorite author",
        ],
        "Sister": [
            "Skincare set", "Trendy accessories", "Concert/event tickets",
            "Personalized jewelry", "Art supplies", "Subscription box",
            "Cozy pajama set", "Photo collage frame",
        ],
        "Brother": [
            "Video game", "Sports equipment", "Tech accessories",
            "Sneakers", "Board game", "Headphones",
            "Funny t-shirt", "Experience gift (escape room, go-kart)",
        ],
        "Grandma": [
            "Photo book of family memories", "Cozy shawl/scarf", "Tea set",
            "Puzzle book", "Garden accessories", "Handmade card + visit",
        ],
        "Grandpa": [
            "Classic book collection", "Comfortable slippers", "Fishing gear",
            "Puzzle/brain teaser", "Photo frame with family picture", "Quality coffee mug",
        ],
    }

    default_suggestions = [
        "Gift card to their favorite store", "Personalized item with their name",
        "Experience gift (dinner, movie, activity)", "Handmade/DIY gift",
        "Subscription service (streaming, magazine)", "Donation to their favorite charity",
    ]

    for member in family:
        name = member["name"]
        relation = member.get("relation", "")
        notes = member.get("notes", "")

        member_suggestions = suggestions.get(relation, default_suggestions)

        console.print(f"\n  [bold cyan]{name}[/bold cyan] ({relation})")
        if notes:
            console.print(f"  [dim]Notes: {notes}[/dim]")
        for s in member_suggestions[:5]:
            console.print(f"    🎁 {s}")


# ═══════════════════════════════════════════════════════════════════════════════
#  MENU
# ═══════════════════════════════════════════════════════════════════════════════

def family_menu():
    """Interactive family helper menu."""
    actions = {
        "1": ("View family members", view_family),
        "2": ("Add family member", add_family_member),
        "3": ("View family events", view_events),
        "4": ("Add family event", add_event),
        "5": ("View errands", view_errands),
        "6": ("Add errand", add_errand),
        "7": ("Complete errand", complete_errand),
        "8": ("View gift ideas", view_gift_ideas),
        "9": ("Add gift idea", add_gift_idea),
        "10": ("Gift suggestion generator", generate_gift_suggestions),
        "0": ("Back to main menu", None),
    }

    while True:
        console.print(Panel("[bold cyan]👨‍👩‍👧‍👦 Family Helper[/bold cyan]", box=box.DOUBLE))
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
