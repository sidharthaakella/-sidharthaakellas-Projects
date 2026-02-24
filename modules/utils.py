"""
TwinBot Utilities — Shared helpers for data persistence, formatting, and date operations.
"""

import json
import os
import csv
from datetime import datetime, timedelta

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)


# ─── JSON Persistence ────────────────────────────────────────────────────────

def data_path(filename: str) -> str:
    """Return the full path to a file inside the data/ directory."""
    return os.path.join(DATA_DIR, filename)


def load_json(filename: str, default=None):
    """Load a JSON file from data/. Returns *default* if the file doesn't exist."""
    path = data_path(filename)
    if not os.path.exists(path):
        return default if default is not None else {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default if default is not None else {}


def save_json(filename: str, data):
    """Save *data* as pretty-printed JSON inside data/."""
    path = data_path(filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str, ensure_ascii=False)


def load_csv(filepath: str) -> list[dict]:
    """Load a CSV file and return a list of row dicts."""
    rows = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


# ─── Date / Time Helpers ─────────────────────────────────────────────────────

def now() -> datetime:
    return datetime.now()


def today_str(fmt: str = "%A, %B %d, %Y") -> str:
    return now().strftime(fmt)


def time_str(fmt: str = "%I:%M %p") -> str:
    return now().strftime(fmt)


def days_until(target_date_str: str, fmt: str = "%Y-%m-%d") -> int:
    """Return the number of days from today until *target_date_str*."""
    target = datetime.strptime(target_date_str, fmt).date()
    delta = target - now().date()
    return delta.days


def friendly_deadline(date_str: str, fmt: str = "%Y-%m-%d") -> str:
    """Return a human-friendly string like '3 days from now' or 'overdue by 2 days'."""
    d = days_until(date_str, fmt)
    if d == 0:
        return "today"
    elif d == 1:
        return "tomorrow"
    elif d > 1:
        return f"in {d} days"
    else:
        return f"overdue by {abs(d)} day{'s' if abs(d) != 1 else ''}"


def parse_date(date_str: str, fmt: str = "%Y-%m-%d") -> datetime:
    return datetime.strptime(date_str, fmt)


# ─── ID Generation ───────────────────────────────────────────────────────────

def generate_id() -> str:
    """Simple timestamp-based unique ID."""
    return now().strftime("%Y%m%d%H%M%S%f")


# ─── Input Helpers ───────────────────────────────────────────────────────────

def safe_input(prompt: str, default: str = "") -> str:
    """Get input with a default fallback."""
    try:
        val = input(prompt).strip()
        return val if val else default
    except (EOFError, KeyboardInterrupt):
        return default


def safe_int_input(prompt: str, default: int = 0) -> int:
    """Get integer input safely."""
    try:
        val = input(prompt).strip()
        return int(val) if val else default
    except (ValueError, EOFError, KeyboardInterrupt):
        return default


def safe_float_input(prompt: str, default: float = 0.0) -> float:
    """Get float input safely."""
    try:
        val = input(prompt).strip()
        return float(val) if val else default
    except (ValueError, EOFError, KeyboardInterrupt):
        return default


def confirm(prompt: str = "Are you sure? (y/n): ") -> bool:
    """Ask for yes/no confirmation."""
    return safe_input(prompt, "n").lower() in ("y", "yes")


# ─── Text Helpers ────────────────────────────────────────────────────────────

def truncate(text: str, length: int = 80) -> str:
    """Truncate text to *length* characters with ellipsis."""
    if len(text) <= length:
        return text
    return text[: length - 3] + "..."


def bullet_list(items: list[str]) -> str:
    """Return a bullet-pointed string."""
    return "\n".join(f"  • {item}" for item in items)


# ─── Motivational Quotes ────────────────────────────────────────────────────

QUOTES = [
    "The secret of getting ahead is getting started. — Mark Twain",
    "It always seems impossible until it's done. — Nelson Mandela",
    "Don't watch the clock; do what it does. Keep going. — Sam Levenson",
    "Success is not final, failure is not fatal: it is the courage to continue that counts. — Winston Churchill",
    "Education is the most powerful weapon which you can use to change the world. — Nelson Mandela",
    "The beautiful thing about learning is that nobody can take it away from you. — B.B. King",
    "You don't have to be great to start, but you have to start to be great. — Zig Ziglar",
    "Believe you can and you're halfway there. — Theodore Roosevelt",
    "The only way to do great work is to love what you do. — Steve Jobs",
    "Your limitation—it's only your imagination.",
    "Push yourself, because no one else is going to do it for you.",
    "Great things never come from comfort zones.",
    "Dream it. Wish it. Do it.",
    "Stay focused and extra sparkly. ✨",
    "The harder you work for something, the greater you'll feel when you achieve it.",
    "Don't stop when you're tired. Stop when you're done.",
    "Wake up with determination. Go to bed with satisfaction.",
    "Do something today that your future self will thank you for.",
    "Little things make big days.",
    "It's going to be hard, but hard does not mean impossible.",
]


def random_quote() -> str:
    import random
    return random.choice(QUOTES)
