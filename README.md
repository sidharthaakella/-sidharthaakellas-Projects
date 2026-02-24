# 🤖 TwinBot — Your Digital Twin

> **Your AI-powered personal assistant that manages your life as a student and a son.**

TwinBot is a comprehensive Python CLI application that acts as your digital twin — handling scheduling, assignments, internet research, family duties, study optimization, and personal organization.

---

## ✨ Features

### 🎓 Student Manager
- **Class Schedule** — Weekly timetable with day/time/room/professor
- **Assignment Tracker** — Track assignments with due dates, priorities, and completion status
- **GPA Calculator** — Record grades and calculate cumulative GPA
- **Exam Countdown** — Schedule exams with live countdown timers
- **Pomodoro Timer** — Built-in study timer (25 min work / 5 min break)

### 📋 Personal Secretary
- **To-Do List** — Priority-based task management with categories
- **Daily Planner** — Plan your day hour by hour
- **Quick Notes** — Save and search notes with tags
- **Reminders** — Set date-based reminders
- **Contacts** — Manage your contact list

### 🌐 Internet Researcher
- **Wikipedia Search** — Look up any topic with full article summaries
- **Wikipedia Deep Dive** — Read specific sections of articles
- **Web Page Reader** — Extract and read content from any URL
- **News Headlines** — Fetch top news from BBC, Reuters, TechCrunch, and more
- **Quick Fact Lookup** — Instant answers via DuckDuckGo
- **Dictionary** — Word definitions, synonyms, and examples
- **Research History** — Automatically saves your research for later reference
- **Bookmarks** — Save URLs for quick access

### 👨‍👩‍👧‍👦 Family Helper
- **Family Members** — Track family contacts with birthdays and notes
- **Family Events** — Schedule and countdown to family events
- **Errands** — Manage family errands with priority levels
- **Gift Ideas** — Save and generate gift suggestions for family members

### 📊 Study Habit Analyzer
- **Dataset Analysis** — Analyze the study habits dataset with statistics
- **Personal Assessment** — Take a quiz to evaluate your study habits
- **Productivity Tips** — Curated tips for better studying
- **Class Comparison** — Compare study patterns across different student types

### 🏠 Life Dashboard
- **Morning Briefing** — Comprehensive daily overview (weather, classes, deadlines, reminders)
- **Quick Stats** — At-a-glance summary of all your data
- **Weather Forecast** — Current weather and 3-day forecast
- **Profile Setup** — Personalize your TwinBot experience

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run TwinBot
python twin_assistant.py
```

### First Run
On your first run, TwinBot will guide you through a quick profile setup:
- Your name and nickname
- School and major
- City (for weather)
- Sleep schedule

---

## 📁 Project Structure

```
├── twin_assistant.py          # Main entry point
├── requirements.txt           # Python dependencies
├── study_habit_classifier_dataset.csv  # Study habits data
├── modules/
│   ├── __init__.py
│   ├── utils.py               # Shared utilities & data persistence
│   ├── student_manager.py     # Class schedule, assignments, GPA, exams
│   ├── personal_secretary.py  # To-dos, planner, notes, reminders
│   ├── internet_researcher.py # Web search, Wikipedia, news, dictionary
│   ├── family_helper.py       # Family events, errands, gift ideas
│   ├── study_analyzer.py      # Study habit analysis & recommendations
│   └── life_dashboard.py      # Daily briefing & weather
└── data/                      # JSON data storage (auto-created)
    ├── profile.json
    ├── schedule.json
    ├── assignments.json
    ├── grades.json
    ├── exams.json
    ├── todos.json
    ├── notes.json
    ├── reminders.json
    ├── contacts.json
    ├── planner.json
    ├── family.json
    ├── family_events.json
    ├── errands.json
    ├── gift_ideas.json
    ├── research_history.json
    └── bookmarks.json
```

---

## 🛠️ Dependencies

| Package | Purpose |
|---------|---------|
| `rich` | Beautiful CLI formatting (tables, panels, colors) |
| `requests` | HTTP requests for web research |
| `beautifulsoup4` | Web page parsing and news feeds |
| `wikipedia-api` | Wikipedia article lookup |
| `pandas` | Data analysis for study habits |
| `schedule` | Task scheduling |

---

## 💡 Tips

- **Start your day** with the Morning Briefing (Main Menu → 1 → 1)
- **Use Quick Actions** (Main Menu → 7) for fast access to common tasks
- **Set up your profile** first for personalized weather and greetings
- **Add your class schedule** to see today's classes in the briefing
- **Track assignments** with due dates to get deadline warnings
- **Use the Pomodoro timer** for focused study sessions
- **Research anything** using Wikipedia, news feeds, or web page reader
- All your data is saved automatically in the `data/` folder

---

## 📝 License

Built with ❤️ for students everywhere. Free to use and modify.
