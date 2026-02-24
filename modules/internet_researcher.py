"""
Internet Researcher — Web search, Wikipedia lookup, news fetching, URL summarizer, data gathering.
Your digital twin for all internet research tasks.
"""

import re
import json
from urllib.parse import quote_plus

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.markdown import Markdown
from rich import box

from modules.utils import load_json, save_json, generate_id, now, truncate

console = Console()

RESEARCH_FILE = "research_history.json"
BOOKMARKS_FILE = "bookmarks.json"

# ─── Dependency checks ───────────────────────────────────────────────────────

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

try:
    import wikipediaapi
    HAS_WIKI = True
except ImportError:
    HAS_WIKI = False


def _check_internet_deps():
    """Warn if internet dependencies are missing."""
    if not HAS_REQUESTS:
        console.print("[red]'requests' library not installed. Run: pip install requests[/red]")
        return False
    return True


# ═══════════════════════════════════════════════════════════════════════════════
#  WIKIPEDIA LOOKUP
# ═══════════════════════════════════════════════════════════════════════════════

def wikipedia_search():
    """Search Wikipedia for a topic and display a summary."""
    if not HAS_WIKI:
        console.print("[red]'wikipedia-api' not installed. Run: pip install wikipedia-api[/red]")
        return

    topic = Prompt.ask("What topic do you want to research?")
    console.print(f"[cyan]Searching Wikipedia for '{topic}'...[/cyan]")

    try:
        wiki = wikipediaapi.Wikipedia(
            user_agent="TwinBot/1.0 (student-assistant)",
            language="en",
        )
        page = wiki.page(topic)

        if not page.exists():
            console.print(f"[yellow]No Wikipedia article found for '{topic}'.[/yellow]")
            # Try search suggestions
            console.print("[dim]Try a different search term or check spelling.[/dim]")
            return

        # Display summary
        summary = page.summary
        if len(summary) > 2000:
            summary = summary[:2000] + "..."

        console.print(Panel(
            f"[white]{summary}[/white]",
            title=f"[bold cyan]📖 Wikipedia: {page.title}[/bold cyan]",
            subtitle=f"[dim]{page.fullurl}[/dim]",
            box=box.ROUNDED,
        ))

        # Show sections
        sections = [s.title for s in page.sections if s.title]
        if sections:
            console.print("\n[bold]Sections:[/bold]")
            for s in sections[:15]:
                console.print(f"  • {s}")
            if len(sections) > 15:
                console.print(f"  ... and {len(sections) - 15} more sections")

        # Save to research history
        _save_research("Wikipedia", topic, summary[:500], page.fullurl)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def wikipedia_deep_dive():
    """Read a specific section of a Wikipedia article."""
    if not HAS_WIKI:
        console.print("[red]'wikipedia-api' not installed. Run: pip install wikipedia-api[/red]")
        return

    topic = Prompt.ask("Wikipedia article title")
    section_name = Prompt.ask("Section name to read")

    try:
        wiki = wikipediaapi.Wikipedia(
            user_agent="TwinBot/1.0 (student-assistant)",
            language="en",
        )
        page = wiki.page(topic)

        if not page.exists():
            console.print(f"[yellow]Article '{topic}' not found.[/yellow]")
            return

        # Find the section
        for section in page.sections:
            if section.title.lower() == section_name.lower():
                text = section.text
                if len(text) > 3000:
                    text = text[:3000] + "..."
                console.print(Panel(
                    f"[white]{text}[/white]",
                    title=f"[bold cyan]{page.title} → {section.title}[/bold cyan]",
                    box=box.ROUNDED,
                ))
                return

        console.print(f"[yellow]Section '{section_name}' not found. Available sections:[/yellow]")
        for s in page.sections:
            console.print(f"  • {s.title}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


# ═══════════════════════════════════════════════════════════════════════════════
#  WEB PAGE READER
# ═══════════════════════════════════════════════════════════════════════════════

def read_webpage():
    """Fetch and extract text content from a URL."""
    if not _check_internet_deps():
        return
    if not HAS_BS4:
        console.print("[red]'beautifulsoup4' not installed. Run: pip install beautifulsoup4[/red]")
        return

    url = Prompt.ask("Enter the URL to read")
    console.print(f"[cyan]Fetching {url}...[/cyan]")

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; TwinBot/1.0; student-assistant)"
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script and style elements
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        # Get title
        title = soup.title.string if soup.title else "No title"

        # Get main text
        text = soup.get_text(separator="\n", strip=True)

        # Clean up excessive whitespace
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = "\n".join(lines)

        if len(clean_text) > 5000:
            clean_text = clean_text[:5000] + "\n\n... [truncated]"

        console.print(Panel(
            f"[white]{clean_text}[/white]",
            title=f"[bold cyan]🌐 {title}[/bold cyan]",
            subtitle=f"[dim]{url}[/dim]",
            box=box.ROUNDED,
        ))

        # Save to research history
        _save_research("Webpage", title, clean_text[:500], url)

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Failed to fetch URL: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Error parsing page: {e}[/red]")


# ═══════════════════════════════════════════════════════════════════════════════
#  NEWS FETCHER
# ═══════════════════════════════════════════════════════════════════════════════

def fetch_news():
    """Fetch top news headlines using a free RSS feed."""
    if not _check_internet_deps():
        return
    if not HAS_BS4:
        console.print("[red]'beautifulsoup4' not installed. Run: pip install beautifulsoup4[/red]")
        return

    sources = {
        "1": ("BBC News", "http://feeds.bbci.co.uk/news/rss.xml"),
        "2": ("Reuters", "http://feeds.reuters.com/reuters/topNews"),
        "3": ("TechCrunch", "https://techcrunch.com/feed/"),
        "4": ("Science Daily", "https://www.sciencedaily.com/rss/all.xml"),
        "5": ("ESPN Sports", "https://www.espn.com/espn/rss/news"),
    }

    console.print("[bold]Available news sources:[/bold]")
    for key, (name, _) in sources.items():
        console.print(f"  [cyan]{key}[/cyan]  {name}")

    choice = Prompt.ask("Choose a source", choices=list(sources.keys()), default="1")
    name, url = sources[choice]

    console.print(f"[cyan]Fetching news from {name}...[/cyan]")

    try:
        headers = {"User-Agent": "TwinBot/1.0"}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")

        if not items:
            # Try HTML parsing as fallback
            soup = BeautifulSoup(response.content, "html.parser")
            items = soup.find_all("item")

        if not items:
            console.print("[yellow]No news items found. The feed might be temporarily unavailable.[/yellow]")
            return

        table = Table(title=f"📰 {name} — Top Headlines", box=box.ROUNDED, show_lines=True)
        table.add_column("#", style="dim", width=4)
        table.add_column("Headline", style="bold white", min_width=40)
        table.add_column("Published", style="yellow")

        for i, item in enumerate(items[:15], 1):
            title = item.find("title")
            pub_date = item.find("pubDate")
            title_text = title.get_text(strip=True) if title else "No title"
            date_text = pub_date.get_text(strip=True)[:20] if pub_date else "—"
            table.add_row(str(i), title_text, date_text)

        console.print(table)

        # Option to read an article
        read_more = Prompt.ask("Enter article number to read more (or 0 to skip)", default="0")
        if read_more != "0":
            idx = int(read_more) - 1
            if 0 <= idx < len(items):
                link = items[idx].find("link")
                if link:
                    link_url = link.get_text(strip=True) or link.get("href", "")
                    if link_url:
                        console.print(f"\n[cyan]Article URL: {link_url}[/cyan]")
                        desc = items[idx].find("description")
                        if desc:
                            desc_text = BeautifulSoup(desc.get_text(), "html.parser").get_text(strip=True)
                            console.print(Panel(desc_text, title="[bold]Article Preview[/bold]", box=box.ROUNDED))

    except Exception as e:
        console.print(f"[red]Error fetching news: {e}[/red]")


# ═══════════════════════════════════════════════════════════════════════════════
#  QUICK FACT LOOKUP
# ═══════════════════════════════════════════════════════════════════════════════

def quick_fact_lookup():
    """Look up a quick fact using DuckDuckGo Instant Answer API."""
    if not _check_internet_deps():
        return

    query = Prompt.ask("What do you want to know?")
    console.print(f"[cyan]Looking up '{query}'...[/cyan]")

    try:
        url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&no_html=1"
        response = requests.get(url, timeout=10)
        data = response.json()

        # Try Abstract first
        abstract = data.get("AbstractText", "")
        abstract_source = data.get("AbstractSource", "")
        abstract_url = data.get("AbstractURL", "")

        if abstract:
            console.print(Panel(
                f"[white]{abstract}[/white]",
                title=f"[bold cyan]💡 {query}[/bold cyan]",
                subtitle=f"[dim]Source: {abstract_source} — {abstract_url}[/dim]",
                box=box.ROUNDED,
            ))
            _save_research("Fact Lookup", query, abstract[:500], abstract_url)
            return

        # Try Answer
        answer = data.get("Answer", "")
        if answer:
            console.print(Panel(
                f"[white]{answer}[/white]",
                title=f"[bold cyan]💡 {query}[/bold cyan]",
                box=box.ROUNDED,
            ))
            _save_research("Fact Lookup", query, answer, "")
            return

        # Try Related Topics
        related = data.get("RelatedTopics", [])
        if related:
            console.print(f"[yellow]No direct answer, but here are related topics:[/yellow]")
            for topic in related[:5]:
                if isinstance(topic, dict) and "Text" in topic:
                    console.print(f"  • {truncate(topic['Text'], 100)}")
            return

        console.print("[yellow]No results found. Try rephrasing your question or use Wikipedia search.[/yellow]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


# ═══════════════════════════════════════════════════════════════════════════════
#  DEFINITION LOOKUP
# ═══════════════════════════════════════════════════════════════════════════════

def definition_lookup():
    """Look up the definition of a word using a free dictionary API."""
    if not _check_internet_deps():
        return

    word = Prompt.ask("Enter a word to define")
    console.print(f"[cyan]Looking up '{word}'...[/cyan]")

    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{quote_plus(word)}"
        response = requests.get(url, timeout=10)

        if response.status_code == 404:
            console.print(f"[yellow]No definition found for '{word}'.[/yellow]")
            return

        data = response.json()
        if not data or not isinstance(data, list):
            console.print("[yellow]Unexpected response format.[/yellow]")
            return

        entry = data[0]
        word_title = entry.get("word", word)
        phonetic = entry.get("phonetic", "")

        console.print(Panel(
            f"[bold]{word_title}[/bold]  {phonetic}",
            title="[bold cyan]📖 Dictionary[/bold cyan]",
            box=box.DOUBLE,
        ))

        for meaning in entry.get("meanings", []):
            part = meaning.get("partOfSpeech", "")
            console.print(f"\n  [bold yellow]{part}[/bold yellow]")
            for i, defn in enumerate(meaning.get("definitions", [])[:3], 1):
                console.print(f"    {i}. {defn['definition']}")
                if defn.get("example"):
                    console.print(f"       [dim italic]Example: \"{defn['example']}\"[/dim italic]")

            synonyms = meaning.get("synonyms", [])
            if synonyms:
                console.print(f"    [green]Synonyms: {', '.join(synonyms[:5])}[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


# ═══════════════════════════════════════════════════════════════════════════════
#  RESEARCH HISTORY & BOOKMARKS
# ═══════════════════════════════════════════════════════════════════════════════

def _save_research(source: str, topic: str, summary: str, url: str):
    """Save a research entry to history."""
    history = load_json(RESEARCH_FILE, default=[])
    history.append({
        "id": generate_id(),
        "source": source,
        "topic": topic,
        "summary": summary[:500],
        "url": url,
        "timestamp": now().isoformat(),
    })
    # Keep last 100 entries
    if len(history) > 100:
        history = history[-100:]
    save_json(RESEARCH_FILE, history)


def view_research_history():
    """Display research history."""
    history = load_json(RESEARCH_FILE, default=[])
    if not history:
        console.print("[yellow]No research history yet. Start exploring![/yellow]")
        return

    table = Table(title="🔬 Research History", box=box.ROUNDED, show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Source", style="cyan")
    table.add_column("Topic", style="bold white")
    table.add_column("Date", style="yellow")
    table.add_column("Summary", style="white")

    for i, entry in enumerate(reversed(history[-20:]), 1):
        table.add_row(
            str(i),
            entry["source"],
            entry["topic"],
            entry["timestamp"][:10],
            truncate(entry.get("summary", ""), 50),
        )

    console.print(table)


def add_bookmark():
    """Save a URL bookmark for later."""
    console.print(Panel("[bold cyan]Add Bookmark[/bold cyan]"))
    title = Prompt.ask("Bookmark title")
    url = Prompt.ask("URL")
    category = Prompt.ask("Category (e.g. Study, Reference, Fun)", default="General")

    bookmarks = load_json(BOOKMARKS_FILE, default=[])
    bookmarks.append({
        "id": generate_id(),
        "title": title,
        "url": url,
        "category": category,
        "added": now().isoformat(),
    })
    save_json(BOOKMARKS_FILE, bookmarks)
    console.print(f"[green]✓ Bookmark saved: '{title}'[/green]")


def view_bookmarks():
    """Display saved bookmarks."""
    bookmarks = load_json(BOOKMARKS_FILE, default=[])
    if not bookmarks:
        console.print("[yellow]No bookmarks saved yet.[/yellow]")
        return

    table = Table(title="🔖 Bookmarks", box=box.ROUNDED, show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Title", style="bold white")
    table.add_column("Category", style="cyan")
    table.add_column("URL", style="blue")

    for i, b in enumerate(bookmarks, 1):
        table.add_row(str(i), b["title"], b.get("category", "—"), truncate(b["url"], 50))

    console.print(table)


# ═══════════════════════════════════════════════════════════════════════════════
#  MENU
# ═══════════════════════════════════════════════════════════════════════════════

def researcher_menu():
    """Interactive internet researcher menu."""
    actions = {
        "1": ("Wikipedia search", wikipedia_search),
        "2": ("Wikipedia deep dive (read section)", wikipedia_deep_dive),
        "3": ("Read a webpage", read_webpage),
        "4": ("Fetch news headlines", fetch_news),
        "5": ("Quick fact lookup", quick_fact_lookup),
        "6": ("Dictionary / definition", definition_lookup),
        "7": ("View research history", view_research_history),
        "8": ("Add bookmark", add_bookmark),
        "9": ("View bookmarks", view_bookmarks),
        "0": ("Back to main menu", None),
    }

    while True:
        console.print(Panel("[bold cyan]🌐 Internet Researcher[/bold cyan]", box=box.DOUBLE))
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
