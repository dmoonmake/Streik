import pytest
from django.urls import reverse
from habits.models import Habit

pytestmark = pytest.mark.django_db

@pytest.fixture
def test_habit():
    """Create a test habit for editing tests."""
    return Habit.objects.create(habit_name="Exercise", habit_occurrence="daily", habit_status="active")

def test_edit_habit(client, test_habit):
    """Test editing a habit updates its details correctly."""
    url = reverse("edit_habit", args=[test_habit.habit_id])
    response = client.post(url, {
        "habit_name": "Morning Jog",
        "habit_occurrence": "daily",
        "habit_status": "active"
    })
    assert response.status_code == 302  # ✅ Redirect after edit

    test_habit.refresh_from_db()
    assert test_habit.habit_name == "Morning Jog"  # ✅ Name should be updated
