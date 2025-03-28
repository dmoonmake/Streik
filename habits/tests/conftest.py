import pytest
from datetime import datetime, timedelta
from habits.models import Habit, Completion

@pytest.fixture
def habit_fixtures(db):
    """
    Creates 5 predefined habits (daily, weekly, monthly) and example completion data
    for each over a 4-week period.
    """
    today = datetime.now().date()

    predefined_habits = [
        {"habit_name": "Exercise", "habit_occurrence": "daily"},
        {"habit_name": "Meditation", "habit_occurrence": "daily"},
        {"habit_name": "Weekly Review", "habit_occurrence": "weekly"},
        {"habit_name": "Budget Check", "habit_occurrence": "monthly"},
        {"habit_name": "Read a Book", "habit_occurrence": "daily"},
    ]

    created_habits = []

    for habit_def in predefined_habits:
        habit = Habit.objects.create(
            habit_name=habit_def["habit_name"],
            habit_occurrence=habit_def["habit_occurrence"],
            habit_status="active"
        )

        # Generate completions
        if habit.habit_occurrence == "daily":
            for i in range(28):  # 4 weeks
                Completion.objects.create(
                    completion_habit_id=habit,
                    completion_date=today - timedelta(days=i)
                )
        elif habit.habit_occurrence == "weekly":
            for i in range(4):
                Completion.objects.create(
                    completion_habit_id=habit,
                    completion_date=today - timedelta(weeks=i)
                )
        elif habit.habit_occurrence == "monthly":
            for i in range(4):
                Completion.objects.create(
                    completion_habit_id=habit,
                    completion_date=today - timedelta(weeks=i * 4)
                )

        created_habits.append(habit)

    return created_habits

# @pytest.fixture
# def test_habit():
#     """
#     Create a test habit for editing tests.
#     """
#     return Habit.objects.create(
#         habit_name="Exercise",
#         habit_occurrence="daily",
#         habit_status="active",
#         habit_best_streak=2,
#         habit_last_streak=2
#     )

# @pytest.fixture
# def today_completion(test_habit):
#     """
#     Create a valid completion for today.
#     """
#     return Completion.objects.create(
#         completion_habit_id=test_habit,
#         completion_date=datetime.now()
#     )

import pytest
from datetime import datetime, timedelta
from habits.models import Habit, Completion
from django.test import Client

@pytest.fixture
def client(db):
    return Client()

@pytest.fixture
def existing_habit(db):
    return Habit.objects.create(
        habit_name="Morning Workout",
        habit_description="Exercise for 30 minutes",
        habit_occurrence="daily",
        habit_status="active",
        habit_last_streak=0,
        habit_best_streak=3
    )

@pytest.fixture
def multiple_habits(db):
    habits = [
        # Active Habits
        Habit.objects.create(habit_name="Evening Run", habit_occurrence="daily", habit_status="active", habit_last_streak=2, habit_best_streak=3),
        Habit.objects.create(habit_name="Weekly Yoga", habit_occurrence="weekly", habit_status="active", habit_last_streak=4, habit_best_streak=5),
        Habit.objects.create(habit_name="Morning Reading", habit_occurrence="daily", habit_status="active", habit_last_streak=1, habit_best_streak=2),

        # Paused Habits (Streaks Frozen)
        Habit.objects.create(habit_name="Museum Visiting", habit_occurrence="monthly", habit_status="paused", habit_last_streak=3, habit_best_streak=8),
        Habit.objects.create(habit_name="Date Night", habit_occurrence="weekly", habit_status="paused", habit_last_streak=5, habit_best_streak=5),
        Habit.objects.create(habit_name="Weekend Hike", habit_occurrence="weekly", habit_status="paused", habit_last_streak=7, habit_best_streak=10),

        # Inactive Habits (Streak Resets)
        Habit.objects.create(habit_name="Swimming", habit_occurrence="daily", habit_status="inactive", habit_last_streak=0, habit_best_streak=6),
        Habit.objects.create(habit_name="Morning Walk", habit_occurrence="daily", habit_status="inactive", habit_last_streak=0, habit_best_streak=4),
        Habit.objects.create(habit_name="Monthly Workshop", habit_occurrence="monthly", habit_status="inactive", habit_last_streak=0, habit_best_streak=3),
    ]

    # Simulate past completions (current streak)
    now = datetime.now()
    
    # Evening Run (2-day streak)
    for i in range(2):
        Completion.objects.create(completion_habit_id=habits[0], completion_date=now - timedelta(days=i))

    # Weekly Yoga (4-week streak)
    for i in range(4):
        Completion.objects.create(completion_habit_id=habits[1], completion_date=now - timedelta(weeks=i))

    # Morning Reading (1-day streak)
    Completion.objects.create(completion_habit_id=habits[2], completion_date=now)

    # Museum Visiting (3-month streak)
    for i in range(3):
        Completion.objects.create(completion_habit_id=habits[3], completion_date=now - timedelta(weeks=i * 4))

    # Date Night (5-week streak)
    for i in range(5):
        Completion.objects.create(completion_habit_id=habits[4], completion_date=now - timedelta(weeks=i))

    # Weekend Hike (7-week streak)
    for i in range(7):
        Completion.objects.create(completion_habit_id=habits[5], completion_date=now - timedelta(weeks=i))

    return habits