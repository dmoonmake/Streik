# Habit Management, Streak Tracking, and Analytics
# As a user, I want to create, edit, and delete a habit, so that I can manage my tracking preferences.
# As a user, I want to mark a habit as completed, so that my streak is updated.
# As a user, I want to see my current streaks, so that I can stay motivated.
# As a user, I want to see if I missed any habits, so that I can improve my consistency.
# As a user, I want to view all my currently tracked habits, so that I can stay aware of my progress.
# As a user, I want to filter habits based on their occurrence (daily, weekly), so that I can focus on specific routines.
# As a user, I want to see which habit has the longest run streak, so that I can identify my most consistent habit.
# As a user, I want to know the longest run streak for a specific habit, so that I can track my record-breaking performance.

Feature: Habit Management, Streak Tracking & Analytics.

    # ✅ Habit Management
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

    # ✅ Streak Tracking
    Scenario: User marks a habit as completed
        Given I have an existing habit
        When I complete the habit for today
        Then my current streak should increase

    Scenario: User sees missed habits
        Given I have an existing habit
        And I missed completing it for a day
        When I visit my habit list
        Then my streak should reset to zero

    # ✅ Analytics & Insights
    Scenario: User views all tracked habits
        Given I have multiple tracked habits
        When I visit my habit list
        Then I should see a list of all my habits

    Scenario: User filters habits by occurrence
        Given I have multiple tracked habits
        When I filter my habits by "daily"
        Then I should only see daily habits

    Scenario: User checks the longest streak for a specific habit
        Given I have multiple tracked habits
        When I view the habit details
        Then I should see its longest recorded streak