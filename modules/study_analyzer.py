"""
Study Analyzer — Analyze study habits from CSV data and provide productivity insights.
Uses the study_habit_classifier_dataset.csv to give personalized recommendations.
"""

import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, FloatPrompt, IntPrompt
from rich import box

from modules.utils import load_csv, BASE_DIR

console = Console()

DATASET_PATH = os.path.join(BASE_DIR, "study_habit_classifier_dataset.csv")


def load_study_data() -> list[dict]:
    """Load the study habits dataset."""
    if not os.path.exists(DATASET_PATH):
        console.print("[red]Study dataset not found at expected path.[/red]")
        return []
    return load_csv(DATASET_PATH)


def dataset_overview():
    """Show an overview of the study habits dataset."""
    data = load_study_data()
    if not data:
        return

    total = len(data)

    # Count study classes
    class_counts = {}
    for row in data:
        cls = row.get("Study_Class", "Unknown")
        class_counts[cls] = class_counts.get(cls, 0) + 1

    # Average hours studied
    hours = [float(row["Hours_Studied"]) for row in data if row.get("Hours_Studied")]
    avg_hours = sum(hours) / len(hours) if hours else 0

    # Average sleep
    sleep = [float(row["Sleep_Hours"]) for row in data if row.get("Sleep_Hours")]
    avg_sleep = sum(sleep) / len(sleep) if sleep else 0

    # Phone distraction rate
    phone_yes = sum(1 for row in data if row.get("Phone_Distracted", "").lower() == "yes")
    phone_rate = (phone_yes / total * 100) if total else 0

    # Break frequency distribution
    break_counts = {}
    for row in data:
        brk = row.get("Break_Frequency", "Unknown")
        break_counts[brk] = break_counts.get(brk, 0) + 1

    # Environment rating average
    env_ratings = [int(row["Env_Rating"]) for row in data if row.get("Env_Rating")]
    avg_env = sum(env_ratings) / len(env_ratings) if env_ratings else 0

    # Display overview
    console.print(Panel("[bold cyan]📊 Study Habits Dataset Overview[/bold cyan]", box=box.DOUBLE))
    console.print(f"  Total records: [bold]{total}[/bold]")
    console.print(f"  Average hours studied: [bold green]{avg_hours:.1f} hrs[/bold green]")
    console.print(f"  Average sleep hours: [bold blue]{avg_sleep:.1f} hrs[/bold blue]")
    console.print(f"  Phone distraction rate: [bold red]{phone_rate:.0f}%[/bold red]")
    console.print(f"  Average environment rating: [bold yellow]{avg_env:.1f}/5[/bold yellow]")

    # Study class distribution
    console.print("\n[bold]Study Class Distribution:[/bold]")
    table = Table(box=box.SIMPLE)
    table.add_column("Study Class", style="cyan")
    table.add_column("Count", style="green", justify="center")
    table.add_column("Percentage", style="yellow", justify="center")
    table.add_column("Bar", style="magenta")

    for cls, count in sorted(class_counts.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        bar = "█" * int(pct / 2)
        table.add_row(cls, str(count), f"{pct:.1f}%", bar)

    console.print(table)

    # Break frequency
    console.print("\n[bold]Break Frequency Distribution:[/bold]")
    for brk, count in sorted(break_counts.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        bar = "█" * int(pct / 2)
        console.print(f"  {brk:12s} {count:3d} ({pct:.0f}%) {bar}")


def analyze_by_class():
    """Detailed analysis broken down by study class."""
    data = load_study_data()
    if not data:
        return

    classes = {}
    for row in data:
        cls = row.get("Study_Class", "Unknown")
        if cls not in classes:
            classes[cls] = []
        classes[cls].append(row)

    for cls, rows in sorted(classes.items()):
        hours = [float(r["Hours_Studied"]) for r in rows]
        sleep = [float(r["Sleep_Hours"]) for r in rows]
        env = [int(r["Env_Rating"]) for r in rows]
        phone_yes = sum(1 for r in rows if r.get("Phone_Distracted", "").lower() == "yes")

        avg_h = sum(hours) / len(hours)
        avg_s = sum(sleep) / len(sleep)
        avg_e = sum(env) / len(env)
        phone_pct = phone_yes / len(rows) * 100

        # Break frequency mode
        breaks = {}
        for r in rows:
            b = r.get("Break_Frequency", "Unknown")
            breaks[b] = breaks.get(b, 0) + 1
        common_break = max(breaks, key=breaks.get)

        console.print(Panel(
            f"  Students: [bold]{len(rows)}[/bold]\n"
            f"  Avg hours studied: [bold]{avg_h:.1f}[/bold]\n"
            f"  Avg sleep: [bold]{avg_s:.1f} hrs[/bold]\n"
            f"  Avg environment rating: [bold]{avg_e:.1f}/5[/bold]\n"
            f"  Phone distraction: [bold]{phone_pct:.0f}%[/bold]\n"
            f"  Most common break pattern: [bold]{common_break}[/bold]",
            title=f"[bold cyan]{cls}[/bold cyan]",
            box=box.ROUNDED,
        ))


def personal_assessment():
    """Interactive personal study habit assessment with recommendations."""
    console.print(Panel(
        "[bold cyan]🔍 Personal Study Habit Assessment[/bold cyan]\n"
        "Answer a few questions and I'll analyze your study habits\n"
        "and give you personalized recommendations.",
        box=box.DOUBLE,
    ))

    hours = FloatPrompt.ask("How many hours do you study per day on average?")
    sleep = FloatPrompt.ask("How many hours of sleep do you get per night?")
    break_freq = Prompt.ask("How often do you take breaks?", choices=["Never", "Sometimes", "Often"])
    phone = Prompt.ask("Are you often distracted by your phone?", choices=["Yes", "No"])
    env_rating = IntPrompt.ask("Rate your study environment (1-5)", default=3)

    # Load dataset for comparison
    data = load_study_data()

    # Find the most similar study class
    best_match = _classify_student(hours, sleep, break_freq, phone, env_rating, data)

    console.print(Panel(
        f"[bold]Your Study Profile:[/bold]\n"
        f"  Hours studied/day: {hours:.1f}\n"
        f"  Sleep hours: {sleep:.1f}\n"
        f"  Break frequency: {break_freq}\n"
        f"  Phone distraction: {phone}\n"
        f"  Environment rating: {env_rating}/5\n\n"
        f"[bold yellow]Predicted Study Class: {best_match}[/bold yellow]",
        title="[bold cyan]📋 Assessment Results[/bold cyan]",
        box=box.DOUBLE,
    ))

    # Generate recommendations
    recommendations = _generate_recommendations(hours, sleep, break_freq, phone, env_rating, best_match)
    console.print(Panel(
        "\n".join(f"  {i}. {rec}" for i, rec in enumerate(recommendations, 1)),
        title="[bold green]💡 Personalized Recommendations[/bold green]",
        box=box.ROUNDED,
    ))


def _classify_student(hours, sleep, break_freq, phone, env_rating, data) -> str:
    """Simple nearest-neighbor classification based on the dataset."""
    if not data:
        # Fallback heuristic
        if hours >= 6 and sleep >= 7 and phone == "No":
            return "Consistent"
        elif hours >= 8 and sleep < 6:
            return "Burnt out"
        elif hours >= 6:
            return "Cramming"
        else:
            return "Unproductive"

    break_map = {"Never": 0, "Sometimes": 1, "Often": 2}
    phone_map = {"No": 0, "Yes": 1}

    user_vec = [
        hours,
        sleep,
        break_map.get(break_freq, 1),
        phone_map.get(phone, 0),
        env_rating,
    ]

    best_dist = float("inf")
    best_class = "Unknown"

    for row in data:
        try:
            row_vec = [
                float(row["Hours_Studied"]),
                float(row["Sleep_Hours"]),
                break_map.get(row.get("Break_Frequency", "Sometimes"), 1),
                phone_map.get(row.get("Phone_Distracted", "No"), 0),
                int(row.get("Env_Rating", 3)),
            ]
            dist = sum((a - b) ** 2 for a, b in zip(user_vec, row_vec))
            if dist < best_dist:
                best_dist = dist
                best_class = row.get("Study_Class", "Unknown")
        except (ValueError, KeyError):
            continue

    return best_class


def _generate_recommendations(hours, sleep, break_freq, phone, env_rating, study_class) -> list[str]:
    """Generate personalized study recommendations."""
    recs = []

    # Hours-based
    if hours < 3:
        recs.append("📚 Try to increase your study time to at least 3-4 hours daily for better results.")
    elif hours < 5:
        recs.append("📚 Your study hours are decent. Try adding 1 more focused hour using the Pomodoro technique.")
    elif hours > 8:
        recs.append("⚠️ You're studying a lot! Make sure you're not burning out — quality > quantity.")

    # Sleep-based
    if sleep < 6:
        recs.append("😴 You're sleep-deprived! Aim for 7-8 hours. Sleep is crucial for memory consolidation.")
    elif sleep < 7:
        recs.append("😴 Try to get at least 7 hours of sleep. Even 30 more minutes can boost focus.")
    elif sleep > 9:
        recs.append("⏰ You might be oversleeping. Try setting a consistent wake-up time.")

    # Break frequency
    if break_freq == "Never":
        recs.append("☕ Take regular breaks! The Pomodoro technique (25 min work / 5 min break) is proven effective.")
    elif break_freq == "Often":
        recs.append("☕ Breaks are good, but make sure they don't eat into your study time. Keep them short (5-10 min).")

    # Phone distraction
    if phone == "Yes":
        recs.append("📱 Phone distraction is your biggest enemy! Try 'Do Not Disturb' mode or leave your phone in another room.")
        recs.append("📱 Consider using app blockers like Forest or Focus Mode during study sessions.")

    # Environment
    if env_rating <= 2:
        recs.append("🏠 Your study environment needs improvement. Try a library, quiet café, or declutter your desk.")
    elif env_rating == 3:
        recs.append("🏠 Your environment is okay but could be better. Good lighting, minimal noise, and a clean desk help a lot.")

    # Class-specific
    if study_class == "Burnt out":
        recs.append("🔥 You show signs of burnout. Take a day off, exercise, and practice self-care. You can't pour from an empty cup.")
    elif study_class == "Unproductive":
        recs.append("🎯 Focus on building a consistent routine. Start small — even 30 minutes of focused study daily builds momentum.")
    elif study_class == "Cramming":
        recs.append("📅 Spread your study sessions throughout the week instead of cramming. Spaced repetition is 3x more effective.")
    elif study_class == "Consistent":
        recs.append("🌟 Great job! You have consistent study habits. Keep it up and consider teaching others — it reinforces your learning!")

    if not recs:
        recs.append("✨ You're doing well! Keep maintaining your current habits and stay consistent.")

    return recs


def productivity_tips():
    """Display general productivity tips for students."""
    tips = [
        ("🍅 Pomodoro Technique", "Study for 25 minutes, break for 5. After 4 cycles, take a 15-30 min break."),
        ("📱 Digital Detox", "Put your phone on airplane mode or in another room while studying."),
        ("📝 Active Recall", "Instead of re-reading, close your notes and try to recall the material from memory."),
        ("🔄 Spaced Repetition", "Review material at increasing intervals: 1 day, 3 days, 1 week, 2 weeks."),
        ("🎯 Eat the Frog", "Do the hardest task first when your energy is highest."),
        ("📊 80/20 Rule", "Focus on the 20% of material that covers 80% of exam questions."),
        ("🏃 Exercise", "30 minutes of exercise boosts focus and memory for hours afterward."),
        ("💤 Sleep Hygiene", "No screens 1 hour before bed. Keep a consistent sleep schedule."),
        ("📖 Feynman Technique", "Explain concepts in simple terms as if teaching a child. Gaps = what to study."),
        ("🎵 Study Music", "Try lo-fi beats, classical music, or nature sounds — avoid music with lyrics."),
        ("🥤 Stay Hydrated", "Dehydration reduces cognitive performance by up to 25%."),
        ("📅 Weekly Review", "Every Sunday, review what you learned and plan the upcoming week."),
    ]

    console.print(Panel("[bold cyan]💡 Productivity Tips for Students[/bold cyan]", box=box.DOUBLE))
    for title, desc in tips:
        console.print(f"  [bold]{title}[/bold]")
        console.print(f"    {desc}\n")


# ═══════════════════════════════════════════════════════════════════════════════
#  MENU
# ═══════════════════════════════════════════════════════════════════════════════

def study_analyzer_menu():
    """Interactive study analyzer menu."""
    actions = {
        "1": ("Dataset overview", dataset_overview),
        "2": ("Analysis by study class", analyze_by_class),
        "3": ("Personal study assessment", personal_assessment),
        "4": ("Productivity tips", productivity_tips),
        "0": ("Back to main menu", None),
    }

    while True:
        console.print(Panel("[bold cyan]📊 Study Habit Analyzer[/bold cyan]", box=box.DOUBLE))
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
