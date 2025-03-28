import pytest
from django.urls import reverse
from datetime import datetime, timedelta
from habits.models import Habit, Completion

pytestmark = pytest.mark.django_db

def test_create_habit_view_post(client):
  """
  Test that a new habit can be created via POST and redirects to habit list.
  """
  response = client.post(reverse("create_habit"), {
    "habit_name": "Test Habit",
    "habit_occurrence": "daily",
    "habit_status": "active"
  })
  assert response.status_code == 302 # Should redirect
  assert response.url == reverse("habit_list") # Check if redirected to habit list
  assert Habit.objects.filter(habit_name="Test Habit").exists() # Check if the habit is created

def test_edit_habit_view_post_name_change(client, habit_fixtures):
  """
  Test editing a habit updates its details correctly.
  """
  test_habit = habit_fixtures[1]  # Pick one habit to edit
  url = reverse("edit_habit", args=[test_habit.habit_id])
  response = client.post(url, {
    "habit_name": "Morning Jog",
    "habit_occurrence": test_habit.habit_occurrence,
    "habit_status": test_habit.habit_status
  })

  assert response.status_code == 302  # Should redirect
  assert response.url == reverse("habit_detail", args=[test_habit.habit_id])  # Check if redirected to habit detail
  test_habit.refresh_from_db() # Check if the habit is updated
  assert test_habit.habit_name == "Morning Jog"  # Name updated

def test_edit_habit_view_post_status_change(client, habit_fixtures):
  """
  Test POST to edit habit with status change to paused.
  """
  test_habit = habit_fixtures[2]  # Pick one habit to edit
  url = reverse("edit_habit", args=[test_habit.habit_id])
  response = client.post(url, {
    "habit_name": test_habit.habit_name,
    "habit_occurrence": test_habit.habit_occurrence,
    "habit_status": "paused"
  })

  assert response.status_code == 302 # Should redirect
  assert response.url == reverse("habit_detail", args=[test_habit.habit_id]) # Check if redirected to habit detail
  test_habit.refresh_from_db() # Check if the habit is updated
  assert test_habit.habit_status == "paused"  # Status updated 

def test_delete_habit_view_post_deletes(client, habit_fixtures):
  """
  Test deleting a habit via POST redirects and removes it from the database.
  """
  test_habit = habit_fixtures[3]  # Pick one habit to delete
  url = reverse("delete_habit", args=[test_habit.habit_id])
  response = client.post(url)

  assert response.status_code == 302 # Should redirect
  assert response.url == reverse("habit_list") # Check if redirected to habit list
  assert not Habit.objects.filter(habit_id=test_habit.habit_id).exists()  # Check if the habit is removed

def test_habit_detail_view_renders(client, habit_fixtures):
  """
  Ensure the habit detail view renders properly for a valid habit.
  """
  test_habit = habit_fixtures[3]  # Pick one habit to view
  url = reverse("habit_detail", args=[test_habit.habit_id])
  response = client.get(url)

  assert response.status_code == 200 # Should return 200 OK
  assert test_habit.habit_name == "Budget Check" # Check if the name is correct
  assert b"Completion History" in response.content  # Check if Complete History is showed

def test_habit_list_view_filters_and_renders(client):
  """
  Test the habit list view with filtering and sorting.
  """
  url = reverse("habit_list")
  response = client.get(url)

  assert response.status_code == 200 # Should return 200 OK
  assert b"active" in response.content # Check if active habits are showed

def test_mark_completed_view_creates_completion(client, habit_fixtures):
  """
  Test marking a habit as completed via POST logic.
  """
  test_habit = habit_fixtures[3]  # Pick one habit 
  url = reverse("mark_completed", args=[test_habit.habit_id])
  response = client.get(url)

  assert response.status_code == 302 # Should redirect
  assert Completion.objects.filter(completion_habit_id=test_habit, completion_deleted=False).exists() # Check if completion is created

def test_analytics_view_renders_successfully(client):
  """
  Test the analytics page loads correctly.
  """
  response = client.get(reverse("analytics"))

  assert response.status_code == 200 # Should return 200 OK
  assert b"Analytics Dashboard" in response.content or b"Longest Run Streak" in response.content # Check if the page is loaded

# GET Requests and Invalid forms
def test_create_habit_view_get(client):
  """
  Test GET request to create_habit view renders the form.
  """
  response = client.get(reverse("create_habit"))

  assert response.status_code == 200 # Should return 200 OK
  assert b"<form" in response.content  # Check is Create form is showed

def test_create_habit_view_invalid_post(client):
  """
  Test POST request to create_habit with invalid data shows errors."
  """
  response = client.post(reverse("create_habit"), {
    "habit_name": "",  # invalid: required field
    "habit_occurrence": "daily",
    "habit_status": "active"
  })

  assert response.status_code == 200 # Should return 200 OK
  assert not Habit.objects.filter(habit_name="").exists()  # Check is empty hame name is created

def test_edit_habit_view_get(client, habit_fixtures):
  """
  Test GET request to edit_habit renders the form with current data.
  """
  test_habit = habit_fixtures[4]  # Pick one habit 
  response = client.get(reverse("edit_habit", args=[test_habit.habit_id]))

  assert response.status_code == 200 # Should return 200 OK
  assert b"<form" in response.content  # Check is Edit form is showed
  assert bytes(test_habit.habit_name, "utf-8") in response.content # Check if the name is correct

def test_edit_habit_view_invalid_post(client, habit_fixtures):
  """
  Test POST with invalid habit form (e.g. blank name) stays on page.
  """
  test_habit = habit_fixtures[4]  # Pick one habit 
  response = client.post(reverse("edit_habit", args=[test_habit.habit_id]), {
    "habit_name": "",  # invalid: required field
    "habit_occurrence": test_habit.habit_occurrence,
    "habit_status": test_habit.habit_status
  })

  assert response.status_code == 200 # Should return 200 OK
  test_habit.refresh_from_db() # Check if the habit is not updated
  assert test_habit.habit_name != ""  # Check if the name is not empty

def test_delete_habit_view_get_confirmation(client, habit_fixtures):
  """
  Test GET request to delete_habit shows the confirmation page.
  """
  test_habit = habit_fixtures[4]  # Pick one habit 
  url = reverse("delete_habit", args=[test_habit.habit_id])
  response = client.get(url)

  assert response.status_code == 200 # Should return 200 OK
  assert bytes(test_habit.habit_name, "utf-8") in response.content # Check if the name is correct

def test_edit_habit_occurrence_resets_streak():
  """
  Test that changing the habit occurrence resets the streak.
  """
  habit = Habit.objects.create(habit_name="Walk", habit_occurrence="daily", habit_status="active")
  now = datetime.now()

  # Create completions for the last 3 days
  Completion.objects.create(completion_habit_id=habit, completion_date=now - timedelta(days=2))
  Completion.objects.create(completion_habit_id=habit, completion_date=now - timedelta(days=1))
  Completion.objects.create(completion_habit_id=habit, completion_date=now)

  assert habit.get_current_streak() == 3 # Streak should be 3 days

  # Simulate user changing occurrence to weekly
  habit.habit_occurrence = "weekly"
  habit.save()

  # Recalculate based on new weekly logic
  streak = habit.get_current_streak()

  # Since completions are close together, it should reset to 1 (same week)
  assert streak == 1 # Streak should be 1 week
  assert habit.habit_last_streak == 1 # Last streak should be 1 week