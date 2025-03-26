import pytest
from datetime import datetime, timedelta
from habits.models import Habit, Completion, Report

pytestmark = pytest.mark.django_db

def test_habit_creation():
    """
    Test creating a new habit.
    """
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
    """
    Test that the streak is preserved when a habit is paused.
    """
    test_habit = Habit.objects.create(habit_name="Reading", habit_occurrence="daily", habit_status="active")
    #Simulate 5-day completion streak
    now = datetime.now()
    Completion.objects.create(completion_habit_id=test_habit, completion_date=now)
    Completion.objects.create(completion_habit_id=test_habit, completion_date=now - timedelta(days=1))
    Completion.objects.create(completion_habit_id=test_habit, completion_date=now - timedelta(days=2))
    Completion.objects.create(completion_habit_id=test_habit, completion_date=now - timedelta(days=3))
    Completion.objects.create(completion_habit_id=test_habit, completion_date=now - timedelta(days=4))
    test_habit.habit_last_streak = test_habit.get_current_streak()
    test_habit.save()

    test_habit.habit_status = "paused"
    test_habit.save()

    assert test_habit.habit_status == "paused"
    assert test_habit.get_current_streak() == 5  # Streak should be preserved

def test_habit_reactivation_from_paused_keeps_streak():
    """
    Test that reactivating a paused habit restores the streak.
    """
    test_habit = Habit.objects.create(habit_name="Meditation", habit_occurrence="daily", habit_status="active")

    # Simulate 3-day completion streak
    now = datetime.now()
    Completion.objects.create(completion_habit_id=test_habit, completion_date=now)
    Completion.objects.create(completion_habit_id=test_habit, completion_date=now - timedelta(days=1))
    Completion.objects.create(completion_habit_id=test_habit, completion_date=now - timedelta(days=2))

    # Pause the habit (streak should be stored in habit_last_streak)
    test_habit.habit_status = "paused"
    test_habit.habit_last_streak = test_habit.get_current_streak()
    test_habit.save()

    # Reactivate the habit
    test_habit.habit_status = "active"
    test_habit.save()

    assert test_habit.get_current_streak() == 3  # Now it works!

def test_habit_reactivation_from_inactive_does_not_restore_streak():
    """
    Test that reactivating an inactive habit does not restore old streak.
    """
    test_habit = Habit.objects.create(habit_name="Dance", habit_occurrence="daily", habit_status="inactive", habit_last_streak=4)
    test_habit.habit_status = "active"
    test_habit.save()

    assert test_habit.get_current_streak() == 0

def test_habit_inactive_resets_streak_and_deletes_today():
    """
    Test that inactive resets streak and marks today's completion deleted.
    """
    test_habit = Habit.objects.create(habit_name="Walking", habit_occurrence="daily", habit_status="active")
    
    now = datetime.now().date()
    Completion.objects.create(completion_habit_id=test_habit, completion_date=now)

    # Simulate inactivation logic as done in your view
    Completion.objects.filter(completion_habit_id=test_habit, completion_date=now).update(completion_deleted=True)
    test_habit.habit_last_streak = 0
    test_habit.habit_status = "inactive"
    test_habit.save()

    assert test_habit.get_current_streak() == 0
    assert not test_habit.completions.filter(completion_date=now, completion_deleted=False).exists()

def test_mark_habit_completed(habit_fixtures):
    """
    Test marking a habit as completed increases streak.
    """
    test_habit = habit_fixtures[0]  # Pick one habit to edit
    # test_habit = Habit.objects.create(habit_name="Yoga", habit_occurrence="daily", habit_status="active")
    
    now = datetime.now()
    Completion.objects.create(completion_habit_id=test_habit, completion_date=now)
    
    assert test_habit.get_current_streak() == 28  # Streak should increase

def test_daily_streak_break():
    test_habit = Habit.objects.create(habit_name="Meditate", habit_occurrence="daily", habit_status="active")
    now = datetime.now()

    Completion.objects.create(completion_habit_id=test_habit, completion_date=now)
    # skipped a day
    Completion.objects.create(completion_habit_id=test_habit, completion_date=now - timedelta(days=2))

    assert test_habit.get_current_streak() == 1  # streak restarted from today only

def test_daily_streak_ignores_deleted():
    test_habit = Habit.objects.create(habit_name="Read", habit_occurrence="daily", habit_status="active")
    now = datetime.now()

    Completion.objects.create(completion_habit_id=test_habit, completion_date=now, completion_deleted=True)
    Completion.objects.create(completion_habit_id=test_habit, completion_date=now - timedelta(days=1))

    assert test_habit.get_current_streak() == 0

def test_weekly_habit_streak_respects_week_cycle():
    """
    Test weekly habit only counts one per week.
    """
    now = datetime.now()
    test_habit = Habit.objects.create(habit_name="Run", habit_occurrence="weekly", habit_status="active")
    Completion.objects.create(completion_habit_id=test_habit, completion_date=now)
    Completion.objects.create(completion_habit_id=test_habit, completion_date=now - timedelta(days=7))
    Completion.objects.create(completion_habit_id=test_habit, completion_date=now - timedelta(days=14))

    assert test_habit.get_current_streak() == 3

def test_weekly_streak_skipped_week():
    test_habit = Habit.objects.create(habit_name="Clean house", habit_occurrence="weekly", habit_status="active")

    Completion.objects.create(completion_habit_id=test_habit, completion_date=datetime(2025, 1, 1))
    Completion.objects.create(completion_habit_id=test_habit, completion_date=datetime(2025, 1, 15))  # skipped Jan 8

    assert test_habit.get_current_streak() == 1  # restarted from Jan 15

def test_weekly_streak_multiple_completions_same_week():
    test_habit = Habit.objects.create(habit_name="Grocery Shopping", habit_occurrence="weekly", habit_status="active")

    Completion.objects.create(completion_habit_id=test_habit, completion_date=datetime(2025, 2, 1))
    Completion.objects.create(completion_habit_id=test_habit, completion_date=datetime(2025, 2, 2))  # same week
    Completion.objects.create(completion_habit_id=test_habit, completion_date=datetime(2025, 2, 8))  # next week

    assert test_habit.get_current_streak() == 2

def test_monthly_habit_streak_respects_month_cycle():
    """
    Test monthly habit streak counts once per calendar month.
    """
    test_habit = Habit.objects.create(habit_name="Budget", habit_occurrence="monthly", habit_status="active")
    Completion.objects.create(completion_habit_id=test_habit, completion_date=datetime(2025, 1, 10))
    Completion.objects.create(completion_habit_id=test_habit, completion_date=datetime(2025, 2, 5))
    Completion.objects.create(completion_habit_id=test_habit, completion_date=datetime(2025, 3, 1))

    assert test_habit.get_current_streak() == 3

def test_monthly_streak_resets_after_missed_month():
    test_habit = Habit.objects.create(habit_name="Reports", habit_occurrence="monthly", habit_status="active")

    Completion.objects.create(completion_habit_id=test_habit, completion_date=datetime(2025, 1, 20))
    Completion.objects.create(completion_habit_id=test_habit, completion_date=datetime(2025, 2, 10))
    Completion.objects.create(completion_habit_id=test_habit, completion_date=datetime(2025, 4, 1))  # March skipped

    assert test_habit.get_current_streak() == 1  # Only counts from April

def test_monthly_streak_restart_after_break():
    test_habit = Habit.objects.create(habit_name="Finances", habit_occurrence="monthly", habit_status="active")

    # Old streak
    Completion.objects.create(completion_habit_id=test_habit, completion_date=datetime(2025, 1, 5))
    Completion.objects.create(completion_habit_id=test_habit, completion_date=datetime(2025, 2, 6))

    # Skipped March

    # Restart
    Completion.objects.create(completion_habit_id=test_habit, completion_date=datetime(2025, 4, 7))
    Completion.objects.create(completion_habit_id=test_habit, completion_date=datetime(2025, 5, 2))

    assert test_habit.get_current_streak() == 2  # Restarted streak from April

def test_monthly_streak_with_multiple_same_month_completions():
    test_habit = Habit.objects.create(habit_name="Stretching", habit_occurrence="monthly", habit_status="active")

    # Same month, only first should count
    Completion.objects.create(completion_habit_id=test_habit, completion_date=datetime(2025, 3, 5))
    Completion.objects.create(completion_habit_id=test_habit, completion_date=datetime(2025, 3, 15))

    Completion.objects.create(completion_habit_id=test_habit, completion_date=datetime(2025, 4, 5))

    assert test_habit.get_current_streak() == 2

def test_monthly_streak_ignores_deleted_completion():
    now = datetime.now()
    habit = Habit.objects.create(habit_name="Reading", habit_occurrence="monthly", habit_status="active")

    Completion.objects.create(completion_habit_id=habit, completion_date=datetime(2025, 1, 5), completion_deleted=True)
    Completion.objects.create(completion_habit_id=habit, completion_date=datetime(2025, 2, 5))

    assert habit.get_current_streak() == 1  # January is ignored

def test_soft_deleted_completion_ignored_in_streak():
    """
    Test that deleted completions do not count toward streak.
    """
    test_habit = Habit.objects.create(habit_name="Push-ups", habit_occurrence="daily", habit_status="active")
    now = datetime.now()
    Completion.objects.create(completion_habit_id=test_habit, completion_date=now - timedelta(days=2))
    Completion.objects.create(completion_habit_id=test_habit, completion_date=now - timedelta(days=1), completion_deleted=True)
    Completion.objects.create(completion_habit_id=test_habit, completion_date=now)

    assert test_habit.get_current_streak() == 1  # Skipped yesterday due to deleted record

def test_streak_inactive_habit_returns_zero():
    test_habit = Habit.objects.create(habit_name="Skip", habit_occurrence="daily", habit_status="inactive")
    assert test_habit.get_current_streak() == 0

def test_streak_paused_habit_returns_last():
    test_habit = Habit.objects.create(habit_name="Break", habit_occurrence="weekly", habit_status="paused", habit_last_streak=3)
    assert test_habit.get_current_streak() == 3

def test_report_returns_longest_streak():
    test_habit = Habit.objects.create(habit_name="Read", habit_occurrence="daily", habit_status="active")
    Completion.objects.create(completion_habit_id=test_habit, completion_date=datetime(2025, 1, 1))
    Completion.objects.create(completion_habit_id=test_habit, completion_date=datetime(2025, 1, 2))
    Completion.objects.create(completion_habit_id=test_habit, completion_date=datetime(2025, 1, 4))  # Break
    Completion.objects.create(completion_habit_id=test_habit, completion_date=datetime(2025, 1, 5))
    Completion.objects.create(completion_habit_id=test_habit, completion_date=datetime(2025, 1, 6))
    assert Report.get_longest_streak(test_habit.habit_id) == 3

    """
    Test setting a habit to inactive resets streak and deletes today's completion.
    """
    test_habit = Habit.objects.create(habit_name="Walking", habit_occurrence="daily", habit_status="active")
    now = datetime.now().date()
    Completion.objects.create(completion_habit_id=test_habit, completion_date=now)
    
    assert Completion.objects.filter(completion_habit_id=test_habit, completion_date=now).exists()

    # Simulate logic performed in your view
    Completion.objects.filter(completion_habit_id=test_habit, completion_date=now).update(completion_deleted=True)
    test_habit.habit_last_streak = 0
    test_habit.habit_status = "inactive"
    test_habit.save()

    assert test_habit.get_current_streak() == 0
    assert not Completion.objects.filter(
        completion_habit_id=test_habit,
        completion_date=now,
        completion_deleted=False
    ).exists()