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

