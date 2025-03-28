import pytest
from habits.forms import HabitForm

pytestmark = pytest.mark.django_db

def test_valid_form_data():
  """
  Test that the form is valid with correct data.
  """
  data = {
    "habit_name": "Read Book",
    "habit_description": "Read every night before bed",
    "habit_occurrence": "daily",
    "habit_status": "active",
  }
  form = HabitForm(data=data)

  assert form.is_valid() # Form should be valid

def test_missing_required_field():
  """
  Test that the form is invalid when a required field is missing.
  """
  data = {
    # "habit_name" is missing
    "habit_description": "No name provided",
    "habit_occurrence": "weekly",
    "habit_status": "paused",
  }
  form = HabitForm(data=data)

  assert not form.is_valid() # Form should be invalid
  assert "habit_name" in form.errors # Check for specific error

def test_invalid_occurrence_value():
  """
  Test that the form is invalid when an invalid occurrence value is provided.
  """
  data = {
    "habit_name": "Weird Habit",
    "habit_description": "Testing invalid occurrence",
    "habit_occurrence": "hourly",  # Invalid choice
    "habit_status": "active",
  }
  form = HabitForm(data=data)

  assert not form.is_valid() # Form should be invalid
  assert "habit_occurrence" in form.errors # Check for specific error

def test_invalid_status_value():
  """
  Test that the form is invalid when an invalid status value is provided.
  """
  data = {
    "habit_name": "Clean Desk",
    "habit_description": "Every week",
    "habit_occurrence": "weekly",
    "habit_status": "snoozed",  # Invalid choice
  }
  form = HabitForm(data=data)

  assert not form.is_valid() # Form should be invalid
  assert "habit_status" in form.errors # Check for specific error

def test_form_initialization_with_instance(existing_habit):
  """
  Test that the form initializes correctly with an existing habit instance.
  """
  form = HabitForm(instance=existing_habit)
  
  assert form.instance == existing_habit # Check if the instance is set correctly
  assert form.initial["habit_name"] == existing_habit.habit_name # Check initial data
  assert form.initial["habit_description"] == existing_habit.habit_description
  assert form.initial["habit_occurrence"] == existing_habit.habit_occurrence
  assert form.initial["habit_status"] == existing_habit.habit_status
