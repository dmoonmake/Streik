# Habit Management
# As a user, I want to create a habit with a name and occurrence, so that I can track it daily or weekly.
# As a user, I want to edit my habit details, so that I can adjust my tracking preferences.
# As a user, I want to remove a habit, so that I don’t see habits that I no longer track.

Feature: Habit Management
    Managing habits including creation, editing, and deletion.

    Scenario: User creates a new habit
        Given I visit the habit creation page
        When I enter habit details
        And I submit the habit form
        Then I should see the new habit in my habit list
    
    Scenario: User edits an existing habit
        Given I have an existing habit
        When I visit the edit page for that habit
        And I update the habit details
        And I submit the edit form
        Then I should see the updated habit in my habit list

    Scenario: User deletes a habit
        Given I have an existing habit
        When I visit the delete page for that habit
        And I confirm the deletion
        Then the habit should no longer exist
