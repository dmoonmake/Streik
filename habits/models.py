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
        Calculates the current streak based on the habit's status and occurrence:
        - If paused, return the last streak before pausing.
        - If inactive, return 0.
        - If active, calculate streak using the occurrence cycle.
        """
        
        # if not valid_completions.exists():
        #     return 0  # No valid completions found

        # if self.habit_status == "inactive":
        #     return 0  # Inactive habits always reset streaks

        # if self.habit_status == "paused":
        #     return self.habit_last_streak  # ⏸ Return last streak before pausing
        
        # # Restore last streak if reactivated
        # if self.habit_status == "active" and self.habit_last_streak > 0:
        #     return self.habit_last_streak 
        
        # completions = self.completions.filter(completion_deleted=False).order_by("-completion_date")

        # if not completions.exists():
        #     return 0  # No completions, streak is 0

        # streak = 0
        # today = date.today()

        # for i, completion in enumerate(completions):
        #     if i == 0 and completion.completion_date == today:
        #         streak += 1
        #     elif i > 0:
        #         expected_date = completions[i - 1].completion_date - timedelta(days=1)
        #         if completion.completion_date == expected_date:
        #             streak += 1
        #         else:
        #             break  # Streak ends if there is a gap

        # # Update best streak if the current streak is higher
        # if streak > self.habit_best_streak:
        #     self.habit_best_streak = streak
        #     self.save()

        # self.habit_last_streak = streak  # ✅ Store streak before pausing
        # self.save()

        # return streak
        if self.habit_status == "inactive":
            return 0

        if self.habit_status == "paused":
            return self.habit_last_streak

        completions = self.completions.filter(completion_deleted=False).order_by("completion_date")
        if not completions.exists():
            return 0

        today = date.today()
        streak = 0

        if self.habit_occurrence == "daily":
            # Consecutive daily completions
            expected_date = today
            valid_dates = [c.completion_date for c in completions]

            while expected_date in valid_dates:
                streak += 1
                expected_date -= timedelta(days=1)

        elif self.habit_occurrence == "weekly":
            # Consecutive weekly buckets (start of the week)
            weeks = []
            for c in completions:
                week_start = c.completion_date - timedelta(days=c.completion_date.weekday())
                if week_start not in weeks:
                    weeks.append(week_start)

            weeks = sorted(weeks, reverse=True)
            current_week = today - timedelta(days=today.weekday())

            for week in weeks:
                if week == current_week:
                    streak += 1
                    current_week -= timedelta(weeks=1)
                else:
                    break

        elif self.habit_occurrence == "monthly":
            # Consecutive calendar months
            months = []
            for c in completions:
                month = (c.completion_date.year, c.completion_date.month)
                if month not in months:
                    months.append(month)

            months = sorted(months, reverse=True)
            current_month = (today.year, today.month)

            for month in months:
                if month == current_month:
                    streak += 1
                    # move to previous month
                    y, m = current_month
                    if m == 1:
                        current_month = (y - 1, 12)
                    else:
                        current_month = (y, m - 1)
                else:
                    break

        # Update last and best streaks
        self.habit_last_streak = streak
        if streak > self.habit_best_streak:
            self.habit_best_streak = streak
        self.save()

        return streak


class Completion(models.Model):
    """
    Represents a record of a habit being completed.

    Attributes:
        completion_id (AutoField): Primary key for Completion.
        completion_habit_id (ForeignKey): Links the completion to a specific Habit.
        completion_date (DateField): The date the habit was completed.
    
    Constraints:
        - unique_together ensures a habit cannot be completed more than once on the same day.
    """

    completion_id = models.AutoField(primary_key=True)
    completion_habit_id = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="completions")
    completion_date = models.DateField(default=date.today)  # Default to today’s date
    completion_deleted = models.BooleanField(default=False)  # Track if completion was deleted

    class Meta:
        unique_together = ("completion_habit_id", "completion_date")  # Prevents duplicate completions for the same day

    def __str__(self):
        return f"{self.completion_habit_id.habit_name} completed on {self.completion_date}"


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

