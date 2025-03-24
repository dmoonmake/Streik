# Streik - Habit Tracker
Django Web Application

A personal habit tracking system built with Django, designed to help users manage daily, weekly, or monthly habits. Users can create, track, complete, and analyse habits over time, with automatic streak calculation and visual analytics powered by Plotly.

---

## 🚀 Features

- **Create / Edit / Delete Habits**
- **Track habits by occurrence** – daily, weekly, monthly
- **Automatic streak tracking** (current & best streaks)
- **Analytics dashboard** with:
  - Habit completion trends
  - Streak visualisation
  - Status breakdown
- Completion disabled if habit is paused/inactive or already completed today

---

## Tech Stack

- **Framework:** Django (Python)
- **Database:** SQLite (default)
- **Frontend:** HTML, CSS, Plotly.js
- **Testing:** Pytest + pytest-bdd (BDD), Unit Tests
- **Visuals:** Plotly + Calplot (calendar visualisation)

---

## 🧪 Testing

### BDD Tests
Located under `habits/tests/features` and `habits/tests/steps`.

Run with:
```bash
pytest

