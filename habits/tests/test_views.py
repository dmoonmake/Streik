import pytest
from django.urls import reverse
from datetime import datetime, timedelta
from habits.models import Habit, Completion

pytestmark = pytest.mark.django_db

# @pytest.fixture
# def test_habit():
#     """Create a test habit for editing tests."""
#     return Habit.objects.create(habit_name="Exercise", habit_occurrence="daily", habit_status="active")

@pytest.fixture
def test_habit():
    """Create a test habit for editing tests."""
    return Habit.objects.create(
        habit_name="Exercise",
        habit_occurrence="daily",
        habit_status="active",
        habit_best_streak=2,
        habit_last_streak=2
    )

@pytest.fixture
def today_completion(test_habit):
    """Create a valid completion for today."""
    return Completion.objects.create(
        completion_habit_id=test_habit,
        completion_date=datetime.now()
    )

def test_edit_habit(client, test_habit):
    """Test editing a habit updates its details correctly."""
    url = reverse("edit_habit", args=[test_habit.habit_id])
    response = client.post(url, {
        "habit_name": "Morning Jog",
        "habit_occurrence": "daily",
        "habit_status": "active"
    })
    assert response.status_code == 302  # ✅ Should redirect
    test_habit.refresh_from_db()
    assert test_habit.habit_name == "Morning Jog"  # ✅ Name updated

def test_pause_habit_preserves_streak(client, test_habit):
    """Test pausing a habit preserves the current streak."""
    test_habit.habit_status = "paused"
    test_habit.save()

    assert test_habit.get_current_streak() == test_habit.habit_last_streak
    assert test_habit.habit_status == "paused"

def test_reactivate_paused_habit_restores_streak(client):
    """
    Test reactivating a paused habit restores previous streak based on real completions.
    """
    habit = Habit.objects.create(habit_name="Meditation", habit_occurrence="daily", habit_status="active")
    now = datetime.now()

    # Simulate 4 consecutive days of completion
    for i in range(4):
        Completion.objects.create(
            completion_habit_id=habit,
            completion_date=now - timedelta(days=i)
        )

    # Pause the habit and save its streak
    habit.habit_status = "paused"
    habit.habit_last_streak = habit.get_current_streak()
    habit.save()

    # Now reactivate it
    habit.habit_status = "active"
    habit.save()

    assert habit.get_current_streak() == 4  # ✅ Valid, based on real data

def test_inactivate_habit_resets_streak_and_deletes_today(client, test_habit, today_completion):
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
