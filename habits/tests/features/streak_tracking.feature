# Streak Tracking
# As a user, I want to mark a habit as completed, so that my streak is updated.
# As a user, I want to see my current streaks, so that I can stay motivated.
# As a user, I want to see if I missed any habits, so that I can improve my consistency.

Feature: Streak Tracking
    Tracking habit completions and streak progress.

    Scenario: User marks a habit as completed
        Given I have an existing habit
        When I complete the habit for today
        Then my current streak should increase

    Scenario: User views their streaks
        Given I have completed a habit multiple days in a row
        When I visit my habit list
        Then I should see my current streak count

    Scenario: User sees missed habits
        Given I have an existing habit
        And I missed completing it for a day
        When I visit my habit list
        Then my streak should reset to zero
