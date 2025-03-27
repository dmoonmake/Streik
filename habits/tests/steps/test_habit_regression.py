import pytest
from pytest_bdd import scenarios, given, when, then

from datetime import datetime, timedelta
from habits.models import Habit, Completion

# Enable database access for all tests in this file
pytestmark = pytest.mark.django_db

# Load the feature file
scenarios("../features/habit_regression.feature")

# Habit Management Steps
@given("I visit the habit creation page")
def visit_habit_page(client):
    response = client.get("/habits/create/")
    assert response.status_code == 200

@when("I enter habit details")
def enter_habit_details(client):
    data = {"habit_name": "Dog Walking", "habit_occurrence": "daily", "habit_status": "active", "habit_last_streak": 0, "habit_best_streak": 0}
    client.post("/habits/create/", data)

@when("I submit the habit form")
def submit_habit_form(client):
    response = client.get("/habits/")
    assert response.status_code == 200

@then("I should see the new habit in my habit list")
def habit_is_created():
    assert Habit.objects.filter(habit_name="Dog Walking").exists()

@given("I have an existing habit")
def habit_exists(existing_habit):
    assert existing_habit is not None

@when("I visit the edit page for that habit")
def visit_edit_page(client, existing_habit):
    response = client.get(f"/habits/{existing_habit.habit_id}/edit/")
    assert response.status_code == 200

@when("I visit the detail page for that habit")
def visit_detail_page(client, existing_habit):
    response = client.get(f"/habits/{existing_habit.habit_id}/")
    assert response.status_code == 200

@when("I update the habit details")
def update_habit_details(client, existing_habit):
    updated_data = {
        "habit_name": "Morning Meditation",
        "habit_description": "Meditate for 15 minutes",
        "habit_occurrence": "daily", 
        "habit_status": "active" 
    }
    client.post(f"/habits/{existing_habit.habit_id}/edit/", updated_data)

@when("I submit the edit form")
def submit_edit_form(client, existing_habit):
    response = client.get("/habits/")
    assert response.status_code == 200

@then("I should see the updated habit in my habit list")
def check_updated_habit():
    assert Habit.objects.filter(habit_name="Morning Meditation").exists()

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

# ✅ Streak Tracking Steps

@when("I complete the habit for today")
def complete_habit_today(existing_habit):
    today = datetime.now()
    Completion.objects.create(completion_habit_id=existing_habit, completion_date=today)

@then("my current streak should increase")
def check_streak(existing_habit):
    assert existing_habit.get_current_streak() > 0

@then("I should see my current streak count")
def check_streak(multiple_habits):
    assert multiple_habits.get_current_streak() > 0

@given("I missed completing it for a day")
def missed_habit(existing_habit):
    today = datetime.now()
    Completion.objects.create(completion_habit_id=existing_habit, completion_date=today - timedelta(days=2))

@then("my streak should reset to zero")
def check_streak_reset(existing_habit):
    assert existing_habit.get_current_streak() == 0

# Analytics & Insights Steps
@given("I have multiple tracked habits")
def multiple_habits_exist(multiple_habits):
    assert len(multiple_habits) > 1

@when("I visit my habit list")
def visit_habit_list(client):
    response = client.get("/habits/")
    assert response.status_code == 200

@then("I should see a list of all my habits")
def check_habit_list(multiple_habits):
    for habit in multiple_habits:
        assert Habit.objects.filter(habit_name=habit.habit_name).exists()

@when('I filter my habits by "daily"')
def filter_habits_by_daily(client):
    response = client.get("/habits/?filter_by=daily")
    assert response.status_code == 200

@then("I should only see daily habits")
def check_filtered_habits():
    assert Habit.objects.filter(habit_occurrence="daily").exists()

@then("I should see the habit with the longest run streak")
def check_longest_streak_habit():
    top_habit = max(Habit.objects.all(), key=lambda h: h.get_current_streak())
    assert top_habit.get_current_streak() > 0

@when("I view the habit details")
def view_habit_details(client, existing_habit):
    response = client.get(f"/habits/{existing_habit.habit_id}/")
    assert response.status_code == 200

@then("I should see its longest recorded streak")
def check_longest_streak(existing_habit):
    assert existing_habit.habit_best_streak >= existing_habit.get_current_streak()

@when("I visit my analytics page")
def visit_analytics_page(client):
    response = client.get("/habits/analytics/")
    assert response.status_code == 200

@when("I visit my analytics page")
def visit_analytics_page(client):
    response = client.get("/habits/analytics/")
    assert response.status_code == 200

@then("I should see the habit with the longest run streak")
def check_longest_streak_habit(multiple_habits):
    top_habit = max(multiple_habits, key=lambda h: h.get_current_streak())
    assert top_habit.get_current_streak() > 0

