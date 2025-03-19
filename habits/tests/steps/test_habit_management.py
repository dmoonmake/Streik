import pytest
from pytest_bdd import scenarios, given, when, then
from django.test import Client
from habits.models import Habit

# ✅ Enable database access for all tests in this file
pytestmark = pytest.mark.django_db

# Load the feature file
scenarios("../features/habit_management.feature")

@pytest.fixture
def client(db):  # ✅ Ensure test database is available
    return Client()

@pytest.fixture
def existing_habit(db):  # ✅ Create a sample habit for testing
    return Habit.objects.create(
        habit_name="Evening Reading",
        habit_description="Read 30 minutes before bed",
        habit_occurrence="daily"
    )

# ✅ Habit Creation Steps
@given("I visit the habit creation page")
def visit_habit_page(client):
    response = client.get("/habits/create/")
    assert response.status_code == 200

@when("I enter habit details")
def enter_habit_details(client):
    data = {
        "habit_name": "Morning Jogging",
        "habit_description": "Run 5km every morning",
        "habit_occurrence": "daily"
    }
    client.post("/habits/create/", data)

@when("I submit the habit form")
def submit_habit_form(client):
    response = client.get("/habits/")
    assert response.status_code == 200

@then("I should see the new habit in my habit list")
def habit_is_created():
    assert Habit.objects.filter(habit_name="Morning Jogging").exists()

# ✅ Habit Editing Steps
@given("I have an existing habit")
def habit_exists(existing_habit):
    assert Habit.objects.filter(habit_name="Evening Reading").exists()

@when("I visit the edit page for that habit")
def visit_edit_page(client, existing_habit):
    response = client.get(f"/habits/{existing_habit.habit_id}/edit/")
    assert response.status_code == 200

@when("I update the habit details")
def update_habit_details(client, existing_habit):
    updated_data = {
        "habit_name": "Morning Meditation",
        "habit_description": "Meditate for 15 minutes",
        "habit_occurrence": "daily"
    }
    client.post(f"/habits/{existing_habit.habit_id}/edit/", updated_data)

@when("I submit the edit form")
def submit_edit_form(client, existing_habit):
    response = client.get("/habits/")
    assert response.status_code == 200

@then("I should see the updated habit in my habit list")
def check_updated_habit():
    assert Habit.objects.filter(habit_name="Morning Meditation").exists()

# ✅ Habit Deletion Steps
@when("I visit the delete page for that habit")
def visit_delete_page(client, existing_habit):
    response = client.get(f"/habits/{existing_habit.habit_id}/delete/")
    assert response.status_code == 200

@when("I confirm the deletion")
def confirm_deletion(client, existing_habit):
    client.post(f"/habits/{existing_habit.habit_id}/delete/")

@then("the habit should no longer exist")
def check_habit_deleted():
    assert not Habit.objects.filter(habit_name="Evening Reading").exists()
