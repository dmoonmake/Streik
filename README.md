# Streik - Habit Tracker  
A **Django Web Application** to help you build, track, and visualise daily, weekly, and monthly habits.

---

## 🚀 Features

- Create, Edit, and Delete Habits
- Track habits by occurrence (daily, weekly, monthly)
- Automatic streak tracking (current & best)
- Analytics dashboard with:
  - Habit completion trends
  - Streak visualisations
  - Status breakdown (active, paused, inactive)
- Completion disabled for paused/inactive habits or if already completed today

---

## 🛠️ Tech Stack

- **Backend:** Django (Python)
- **Database:** SQLite (default)
- **Frontend:** HTML, CSS, JScript
- **Testing:** Pytest + Pytest-BDD (for BDD and Unit Tests)
- **Visualisation:** Plotly

---

## 💻 Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/streik.git
cd streik
```

2. **Create and activate a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # For Mac/Linux
venv\Scripts\activate     # For Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Apply migrations**
```bash
python manage.py migrate
```

5. **Seed sample data (optional)**
```bash
python manage.py seed_habits
```

6. **Run the development server**
```bash
python manage.py runserver
```

---

## 🧪 Testing

### Unit Tests
- Located in:
  - `habits/tests/unit/test_models.py`
  - `habits/tests/unit/test_views.py`
  - `habits/tests/unit/test_forms.py`

### BDD Tests (Behaviour-Driven Development)
- **Feature files:** `habits/tests/features/`
- **Step definitions:** `habits/tests/steps/`
- **Shared fixtures:** `conftest.py`

Run all tests:
```bash
pytest
```

Run a specific test file:
```bash
pytest habits/tests/unit/test_models.py
```

### 📁 Project Structure

```
habits/
├── management/commands/
│   └── seed_habits.py       # Example data
├── migrations/
├── static/
├── templates/
├── tests/
|   └── unit
│     ├── test_models.py       # Unit tests for models
│     ├── test_views.py        # Unit tests for views
│     ├── test_forms.py        # Unit tests for forms
│     ├── features/            # .feature files for BDD
│     └── steps/               # Step definitions for BDD
```

---


