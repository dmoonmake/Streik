from django.db import models
from datetime import date, timedelta

class Habit(models.Model):
    """
    Represents a habit that a user wants to track.

    Attributes:
        habit_id (AutoField): Primary key for the Habit.
        habit_name (CharField): The name/title of the habit.
        habit_description (TextField): Additional details about the habit (optional).
        habit_occurrence (CharField): How often the habit occurs (Daily, Weekly, Monthly).
        habit_created_on (DateTimeField): The date when the habit was created.
    """

    habit_id = models.AutoField(primary_key=True)
    habit_name = models.CharField(max_length=255)
    habit_description = models.TextField(blank=True, null=True)  # Optional description
    habit_occurrence = models.CharField(
        max_length=20,
        choices=[("daily", "Daily"), ("weekly", "Weekly"), ("monthly", "Monthly")],
        default="daily"  # Default to daily occurrence
    )
    habit_created_on = models.DateTimeField(auto_now_add=True)  # Auto set when habit is created
    habit_best_streak = models.IntegerField(default=0)
    
    STATUS_CHOICES = [
        ("active", "Active"),       # Currently being tracked
        ("paused", "Paused"),       # Temporarily stopped but streaks are saved
        ("inactive", "Inactive"),   # Stopped tracking, streak resets
    ]
    habit_status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default="active"
    ) 
    habit_last_streak = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.habit_name} ({self.habit_occurrence})"
    
    def get_current_streak(self):
        """
        Calculates the current streak based on the last completed habit tracking.
        - If Paused, return the last known streak before pausing.
        - If Inactive, reset streak to 0.
        - If Active, return the current streak.
        """

        if self.habit_status == "inactive":
            return 0  # Inactive habits always reset streaks

        if self.habit_status == "paused":
            return self.habit_last_streak  # ⏸ Return last streak before pausing
        
        completions = self.completions.order_by("-completion_date")

        if not completions.exists():
            return 0  # No completions, streak is 0

        streak = 0
        today = date.today()

        for i, completion in enumerate(completions):
            if i == 0 and completion.completion_date == today:
                streak += 1
            elif i > 0:
                expected_date = completions[i - 1].completion_date - timedelta(days=1)
                if completion.completion_date == expected_date:
                    streak += 1
                else:
                    break  # Streak ends if there is a gap

        # Update best streak if the current streak is higher
        if streak > self.habit_best_streak:
            self.habit_best_streak = streak
            self.save()

        return streak


class Completion(models.Model):
    """
    Represents a record of a habit being completed.

    Attributes:
        completion_id (AutoField): Primary key for Completion.
        completion_habit (ForeignKey): Links the completion to a specific Habit.
        completion_date (DateField): The date the habit was completed.
    
    Constraints:
        - unique_together ensures a habit cannot be completed more than once on the same day.
    """

    completion_id = models.AutoField(primary_key=True)
    completion_habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="completions")
    completion_date = models.DateField(default=date.today)  # Default to today’s date

    class Meta:
        unique_together = ("completion_habit", "completion_date")  # Prevents duplicate completions for the same day

    def __str__(self):
        return f"{self.completion_habit.habit_name} completed on {self.completion_date}"


class Report:
    """
    A utility class that provides methods to generate habit reports.

    Methods:
        get_longest_streak(habit_id: int) -> int:
            Computes the longest streak of consecutive completions for a given habit.
    """

    @staticmethod
    def get_longest_streak(habit_id: int) -> int:
        """
        Calculates the longest consecutive streak of completions for a given habit.

        :param habit_id: The ID of the habit.
        :return: The longest streak count.
        """
        try:
            habit = Habit.objects.get(habit_id=habit_id)
            completions = habit.completions.order_by("completion_date")

            if not completions.exists():
                return 0

            longest_streak = 0
            current_streak = 1
            prev_date = completions.first().completion_date

            for completion in completions[1:]:
                if completion.completion_date == prev_date + timedelta(days=1):
                    current_streak += 1
                else:
                    longest_streak = max(longest_streak, current_streak)
                    current_streak = 1  # Reset streak if there's a gap

                prev_date = completion.completion_date

            return max(longest_streak, current_streak)  # Return the longest streak found

        except Habit.DoesNotExist:
            return 0  # If the habit doesn't exist, return 0

