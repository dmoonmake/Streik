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
    #Simulate 5-day completion streak
    today = date.today()
    Completion.objects.create(completion_habit_id=habit, completion_date=today)
    Completion.objects.create(completion_habit_id=habit, completion_date=today - timedelta(days=1))
    Completion.objects.create(completion_habit_id=habit, completion_date=today - timedelta(days=2))
    Completion.objects.create(completion_habit_id=habit, completion_date=today - timedelta(days=3))
    Completion.objects.create(completion_habit_id=habit, completion_date=today - timedelta(days=4))
    habit.habit_last_streak = habit.get_current_streak()
    habit.save()

    habit.habit_status = "paused"
    habit.save()

    assert habit.get_current_streak() == 5  # ✅ Streak should be preserved

def test_habit_reactivation_from_paused_keeps_streak():
    """Test that reactivating a paused habit restores the streak."""
    habit = Habit.objects.create(habit_name="Meditation", habit_occurrence="daily", habit_status="active")

    # Simulate 3-day completion streak
    today = date.today()
    Completion.objects.create(completion_habit_id=habit, completion_date=today)
    Completion.objects.create(completion_habit_id=habit, completion_date=today - timedelta(days=1))
    Completion.objects.create(completion_habit_id=habit, completion_date=today - timedelta(days=2))

    # Pause the habit (streak should be stored in habit_last_streak)
    habit.habit_status = "paused"
    habit.habit_last_streak = habit.get_current_streak()
    habit.save()

    # Reactivate the habit
    habit.habit_status = "active"
    habit.save()

    assert habit.get_current_streak() == 3  # ✅ Now it works!

def test_habit_reactivation_from_inactive_does_not_restore_streak():
    """Test that reactivating an inactive habit does not restore old streak."""
    habit = Habit.objects.create(habit_name="Dance", habit_occurrence="daily", habit_status="inactive", habit_last_streak=4)
    habit.habit_status = "active"
    habit.save()

    assert habit.get_current_streak() == 0

def test_habit_inactive_resets_streak_and_deletes_today():
    """Test that inactive resets streak and marks today's completion deleted."""
    habit = Habit.objects.create(habit_name="Walking", habit_occurrence="daily", habit_status="active")
    Completion.objects.create(completion_habit_id=habit, completion_date=date.today())

    # Simulate inactivation logic as done in your view
    Completion.objects.filter(completion_habit_id=habit, completion_date=date.today()).update(completion_deleted=True)
    habit.habit_last_streak = 0
    habit.habit_status = "inactive"
    habit.save()

    assert habit.get_current_streak() == 0
    assert not habit.completions.filter(completion_date=date.today(), completion_deleted=False).exists()

def test_mark_habit_completed():
    """Test marking a habit as completed increases streak."""
    habit = Habit.objects.create(habit_name="Yoga", habit_occurrence="daily", habit_status="active")
    
    today = date.today()
    Completion.objects.create(completion_habit_id=habit, completion_date=today)
    
    assert habit.get_current_streak() == 1  # ✅ Streak should increase

def test_daily_habit_streak_multiple_days():
    """Test daily streak increases with consecutive days."""
    habit = Habit.objects.create(habit_name="Yoga", habit_occurrence="daily", habit_status="active")
    today = date.today()
    Completion.objects.create(completion_habit_id=habit, completion_date=today)
    Completion.objects.create(completion_habit_id=habit, completion_date=today - timedelta(days=1))
    Completion.objects.create(completion_habit_id=habit, completion_date=today - timedelta(days=2))

    assert habit.get_current_streak() == 3

def test_weekly_habit_streak_respects_week_cycle():
    """Test weekly habit only counts one per week."""
    habit = Habit.objects.create(habit_name="Run", habit_occurrence="weekly", habit_status="active")
    Completion.objects.create(completion_habit_id=habit, completion_date=date.today())
    Completion.objects.create(completion_habit_id=habit, completion_date=date.today() - timedelta(days=7))
    Completion.objects.create(completion_habit_id=habit, completion_date=date.today() - timedelta(days=14))

    assert habit.get_current_streak() == 3

def test_monthly_habit_streak_respects_month_cycle():
    """Test monthly habit streak counts once per calendar month."""
    habit = Habit.objects.create(habit_name="Budget", habit_occurrence="monthly", habit_status="active")
    Completion.objects.create(completion_habit_id=habit, completion_date=date(2025, 1, 10))
    Completion.objects.create(completion_habit_id=habit, completion_date=date(2025, 2, 5))
    Completion.objects.create(completion_habit_id=habit, completion_date=date(2025, 3, 1))

    assert habit.get_current_streak() == 3

def test_soft_deleted_completion_ignored_in_streak():
    """Test that deleted completions do not count toward streak."""
    habit = Habit.objects.create(habit_name="Push-ups", habit_occurrence="daily", habit_status="active")
    today = date.today()
    Completion.objects.create(completion_habit_id=habit, completion_date=today - timedelta(days=2))
    Completion.objects.create(completion_habit_id=habit, completion_date=today - timedelta(days=1), completion_deleted=True)
    Completion.objects.create(completion_habit_id=habit, completion_date=today)

    assert habit.get_current_streak() == 1  # Skipped yesterday due to deleted record
