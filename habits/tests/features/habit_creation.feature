Feature: Habit Management
    As a user
    I want to create a new habit
    So that I can track my progress

    Scenario: User creates a new habit
        Given I visit the habit creation page
        When I fill in the habit details
        And I submit the form
        Then I should see the new habit in my habit list
