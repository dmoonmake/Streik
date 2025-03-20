import pytest
from datetime import date, timedelta
from habits.models import Habit, Completion

pytestmark = pytest.mark.django_db

def test_habit_creation():
    """Test creating a new habit."""
    habit = Habit.objects.create(
        habit_name="Exercise",
        habit_description="Morning workout",
        habit_occurrence="daily",
        habit_status="active",
        habit_best_streak=0,
        habit_last_streak=0
    )
    assert habit.habit_name == "Exercise"
    assert habit.habit_status == "active"

def test_habit_streak_preserved_when_paused():
    """Test that the streak is preserved when a habit is paused."""
    habit = Habit.objects.create(habit_name="Reading", habit_occurrence="daily", habit_status="active")
    habit.habit_last_streak = 5  # Pretend user had a 5-day streak
    habit.save()

    # Pause the habit
    habit.habit_status = "paused"
    habit.save()

    assert habit.get_current_streak() == 5  # ✅ Streak should be frozen

def test_habit_reactivation_keeps_streak():
    """Test that reactivating a paused habit restores the streak."""
    habit = Habit.objects.create(habit_name="Meditation", habit_occurrence="daily", habit_status="active")
    habit.habit_last_streak = 3
    habit.save()

    # Paused the habit
    habit.habit_status = "paused"
    habit.save()

    # Activate the habit
    habit.habit_status = "active"
    habit.save()

    assert habit.get_current_streak() == 3  # ✅ Streak should continue from 3

def test_habit_inactive_resets_streak():
    """Test that setting a habit to inactive resets the streak."""
    habit = Habit.objects.create(habit_name="Walking", habit_occurrence="weekly", habit_status="active")
    habit.habit_last_streak = 4
    habit.save()

    # Inactivate the habit
    habit.habit_status = "inactive"
    habit.save()

    assert habit.get_current_streak() == 0  # ✅ Streak should reset to 0

def test_mark_habit_completed():
    """Test marking a habit as completed increases streak."""
    habit = Habit.objects.create(habit_name="Yoga", habit_occurrence="daily", habit_status="active")
    
    today = date.today()
    Completion.objects.create(completion_habit_id=habit, completion_date=today)
    
    assert habit.get_current_streak() == 1  # ✅ Streak should increase
