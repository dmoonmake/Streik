import pytest
from pytest_bdd import scenarios, given, when, then
from django.test import Client
from habits.models import Habit

# ✅ Enable database access for all tests in this file
pytestmark = pytest.mark.django_db

# Load the feature file
scenarios("../features/habit_creation.feature")

@pytest.fixture
def client(db):  # Ensure test database is available
    return Client()

@given("I visit the habit creation page")
def visit_habit_page(client):
    response = client.get("/habits/create/")
    assert response.status_code == 200

@when("I fill in the habit details")
def fill_habit_form(client):
    data = {
        "habit_name": "Morning Jogging",
        "habit_description": "Run 5km every morning",
        "habit_occurrence": "daily"
    }
    response = client.post("/habits/create/", data)
    assert response.status_code == 302  # ✅ Expect redirect

@when("I submit the form")  # ✅ Add this missing step
def submit_form(client):
    response = client.get("/habits/")
    assert response.status_code == 200  # ✅ Expect habit list page to load

@then("I should see the new habit in my habit list")
def habit_is_created():
    assert Habit.objects.filter(habit_name="Morning Jogging").exists()
