
from datetime import timedelta, datetime
from django.db import models
from django.db.models import Max, Count
import plotly.graph_objects as go

class Habit(models.Model):
    """
    Represents a habit that a user wants to track.

    Attributes:
        habit_id (AutoField): Primary key for the Habit.
        habit_name (CharField): The name/title of the habit.
        habit_description (TextField): Additional details about the habit (optional).
        habit_occurrence (CharField): How often the habit occurs (Daily, Weekly, Monthly).
        habit_created_on (DateTimeField): The date when the habit was created.
        habit_best_streak (IntegerField): The longest streak of consecutive completions.
        habit_status (CharField): The current status of the habit (Active, Paused, Inactive).
        habit_last_streak (IntegerField): The most recent streak of consecutive completions.

    Methods:
        __str__() -> str: Returns a string representation of the habit.
        _calculate_daily_streak(completions, today) -> int: Calculate the current streak for a daily habit.
        _calculate_monthly_streak(completions) -> int: Calculate the current streak for a monthly habit.
        _calculate_weekly_streak(completions) -> int: Calculate the current streak for a weekly habit.
        _update_streaks(streak) -> None: Update the habit's last and best streaks.
        get_current_streak() -> int: Calculate the current streak based on the habit's status and occurrence.
    """

    habit_id = models.AutoField(primary_key=True)
    habit_name = models.CharField(max_length=255)
    habit_description = models.TextField(blank=True, null=True)  # Optional description
    
    OCCURENCE_CHOICES = [
        ("daily", "Daily"),     
        ("weekly", "Weekly"), 
        ("monthly", "Monthly"),
    ]
    habit_occurrence = models.CharField(
        max_length = 20,
        choices = OCCURENCE_CHOICES,
        default = "daily"  # Default to daily occurrence
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
        """
        Returns a string representation of the habit.
        """
        return f"{self.habit_name} ({self.habit_occurrence})"

    def _calculate_daily_streak(self, completions, today):
        """
        Calculate the current streak for a daily habit.

        Args:
            completions (QuerySet): The list of completions for the habit.
            today (date): The current date.

        Returns:
            int: The current streak count.
        """
        expected_date = datetime.today().date()
        
        valid_dates = {c.completion_date.date() for c in completions}

        streak = 0
        while expected_date in valid_dates:
            streak += 1
            expected_date -= timedelta(days=1)

        self._update_streaks(streak)
        return streak

    def _calculate_monthly_streak(self, completions):
        """
        Calculate the current streak for a monthly habit.

        Args:
            completions (QuerySet): The list of completions for the habit.

        Returns:
            int: The current streak count.
        """
        streak = 1
        expected_next = completions[0].completion_date.replace(day=1) + timedelta(days=32)
        expected_next = expected_next.replace(day=1)

        for i in range(1, len(completions)):
            current_month = completions[i].completion_date.replace(day=1)   # Get the first day of the month

            if expected_next <= current_month < expected_next + timedelta(days=31): 
                streak += 1
                expected_next = expected_next.replace(day=1) + timedelta(days=32) 
                expected_next = expected_next.replace(day=1)
            elif current_month >= expected_next + timedelta(days=31): # Gap found
                streak = 1
                expected_next = current_month.replace(day=1) + timedelta(days=32)
                expected_next = expected_next.replace(day=1)

        self._update_streaks(streak)
        return streak

    def _calculate_weekly_streak(self, completions):
        """
        Calculate the current streak for a weekly habit.

        Args:
            completions (QuerySet): The list of completions for the habit.

        Returns:
            int: The current streak count.
        """
        streak = 1
        cycle_start = completions[0].completion_date.date()
        expected_next = cycle_start + timedelta(weeks=1)

        # Check each completion to determine the streak
        for i in range(1, len(completions)):
            if expected_next <= completions[i].completion_date.date() < expected_next + timedelta(days=7): 
                streak += 1
                expected_next += timedelta(weeks=1)
            elif completions[i].completion_date.date() >= expected_next + timedelta(days=7): # Gap found
                streak = 1
                expected_next = completions[i].completion_date.date() + timedelta(weeks=1)

        self._update_streaks(streak)
        return streak

    def _update_streaks(self, streak):
        """
        Update the habit's last and best streaks.

        Args:
            streak (int): The current streak count.
        """
        self.habit_last_streak = streak
        if streak > self.habit_best_streak:
            self.habit_best_streak = streak
        self.save()

    def get_current_streak(self):
        """
        Calculates the current streak based on the habit's status and occurrence:
        - If inactive, return 0.
        - If paused, return the last streak before pausing.
        - If active, calculate streak using the occurrence cycle:
            - daily: at midnight
            - weekly: 7 days after completion
            - monthly: at the 1st of each month
        - Returns the current streak count.
        """
        if self.habit_status == "inactive":
            self.habit_last_streak = 0
            self.save(update_fields=["habit_last_streak"])
            return 0

        if self.habit_status == "paused":
            return self.habit_last_streak

        completions = list(
            self.completions.filter(completion_deleted=False).order_by("completion_date")
        )

        now = datetime.now()

        if self.habit_occurrence == "daily":
            streak = self._calculate_daily_streak(completions, now)
        elif self.habit_occurrence == "weekly":
            streak = self._calculate_weekly_streak(completions)
        elif self.habit_occurrence == "monthly":
            streak = self._calculate_monthly_streak(completions)
        else:
            streak = 0

        if streak > self.habit_best_streak:
            self.habit_best_streak = streak

        self.habit_last_streak = streak
        self.save(update_fields=["habit_last_streak", "habit_best_streak"])
        return streak

class Completion(models.Model):
    """
    Represents a record of a habit being completed.

    Attributes:
        completion_id (AutoField): Primary key for Completion.
        completion_habit_id (ForeignKey): Links the completion to a specific Habit.
        completion_date (DateTimeField): The date the habit was completed.
        completion_deleted (BooleanField): Tracks if the completion was deleted.
    
    Constraints:
        - unique_together ensures a habit cannot be completed more than once on the same day.

    Methods:
        __str__() -> str: Returns a string representation of the completion.
    """

    completion_id = models.AutoField(primary_key=True)
    completion_habit_id = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="completions")
    completion_date = models.DateTimeField(default=datetime.now)  # Default to now
    completion_deleted = models.BooleanField(default=False)  # Track if completion was deleted

    class Meta:
        unique_together = ("completion_habit_id", "completion_date")  # Prevents duplicate completions for the same day

    def __str__(self):
        """
        Returns a string representation of the completion.
        """
        return f"{self.completion_habit_id.habit_name} completed on {self.completion_date}"

class Report:
    """
    A utility class that provides methods to generate habit reports.

    Methods:
        filter_habits_by_occurrence(occurrence: str) -> QuerySet: Filters habits by their occurrence type.
        generate_completion_chart(completions, habit_name) -> str: Generates a Plotly bar chart for a habit.
        generate_completion_trend_chart() -> str: Generates a Plotly Line Chart for Completion Trends.
        generate_status_chart() -> str: Generates a Plotly Pie Chart for Habit Statuses.
        generate_streak_chart() -> str: Generates a Plotly Bar Chart for Habit Streaks.
        get_longest_streak(habit_id: int) -> int: Calculates the longest consecutive streak for a habit.
        habits_completed_count() -> tuple: Returns the count of habits that have been completed.
    """
      
    @staticmethod
    def filter_habits_by_occurrence(occurrence: str):
        """
        Filters habits by their occurrence type (daily, weekly, monthly).

        Args:
            occurrence (str): The occurrence type to filter by.

        Returns:
            QuerySet: The filtered habits.
        """
        if occurrence in ["daily", "weekly", "monthly"]:
            return Habit.objects.filter(habit_occurrence=occurrence) 
        return Habit.objects.all()

    @staticmethod
    def generate_completion_chart(completions, habit_name):
        """
        Generates a Plotly bar chart for an individual habit's completion history.

        Args:
            completions (QuerySet): The list of completions for the habit.
            habit_name (str): The name of the habit.

        Returns:
            str: The HTML representation of the chart.
        """
        dates = [c.completion_date.date().strftime("%Y-%m-%d") for c in completions]
        counts = [1] * len(dates)  # Each completion is counted as 1

        fig = go.Figure()
        fig.add_trace(go.Bar(x=dates, y=counts, marker_color="blue"))
        fig.update_layout(
            title=f"Completion History for {habit_name}",
            xaxis_title="Date",
            yaxis_title="Completed",
            yaxis=dict(tickvals=[1], ticktext=["✔"]),
            height=300
        )

        return fig.to_html(full_html=False)
    
    @staticmethod
    def generate_completion_trend_chart():
        """
        Generate a Plotly Line Chart for Completion Trends Over Time.

        Returns:
            str: The HTML representation of the chart.
        """
        completions = Completion.objects.filter(completion_deleted=False).values("completion_date").annotate(
            count=models.Count("completion_id")
        ).order_by("completion_date")

        dates = [item["completion_date"].strftime("%Y-%m-%d") for item in completions]
        counts = [item["count"] for item in completions]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=counts, mode="lines+markers", name="Completions"))
        fig.update_layout(title="Habit Completion Trends", xaxis_title="Date", yaxis_title="Completions")

        return fig.to_html(full_html=False)

    @staticmethod
    def generate_status_chart():
        """
        Generates a Plotly Pie Chart for Habit Statuses.

        Returns:
            str: The HTML representation of the chart.
        """
        habits = Habit.objects.all()
        status_counts = {
            "Active": habits.filter(habit_status="active").count(),
            "Paused": habits.filter(habit_status="paused").count(),
            "Inactive": habits.filter(habit_status="inactive").count(),
        }

        fig = go.Figure(data=[go.Pie(
            labels=list(status_counts.keys()),
            values=list(status_counts.values()),
            marker=dict(colors=["#4CAF50", "#FFC107", "#F44336"])
        )])

        fig.update_layout(title="Habit Status Breakdown")
        return fig.to_html(full_html=False)

    @staticmethod
    def generate_streak_chart():
        """
        Generates a Plotly Bar Chart for Habit Streaks.

        Returns:
            str: The HTML representation of the chart.
        """
        habits = Habit.objects.all().order_by("-habit_best_streak")[:5]  # Top 5 habits by streak

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[habit.habit_name for habit in habits], 
            y=[habit.habit_best_streak for habit in habits],
            name="Best Streak", marker_color="#007BFF"
        ))

        fig.add_trace(go.Bar(
            x=[habit.habit_name for habit in habits], 
            y=[habit.get_current_streak() for habit in habits],
            name="Current Streak", marker_color="#34A853"
        ))

        fig.update_layout(
            title="Habit Streak Trends",
            xaxis_title="Habits",
            yaxis_title="Number of Days",
            barmode="group"
        )

        return fig.to_html(full_html=False)

    @staticmethod
    def get_habits_with_longest_streak():
        """
        Finds all habits that currently have the longest streak.

        Returns:
            QuerySet: The habits with the longest streak.
        """
        max_streak = Habit.objects.aggregate(max_streak=Max("habit_best_streak"))["max_streak"]
        
        if max_streak is None:  # Handle case when no habits exist
            return []

        return Habit.objects.filter(habit_best_streak=max_streak)
    
    @staticmethod
    def get_longest_streak(habit_id: int) -> int:
        """
        Calculates the longest consecutive streak of completions for a given habit.

        Args:
            habit_id (int): The ID of the habit.

        Returns:
            int: The longest streak count.
        """
        try:
                
            habit = Habit.objects.get(habit_id=habit_id)
            completions = habit.completions.filter(completion_deleted=False).order_by("completion_date")

            if not completions:
                return 0

            longest_streak = 1
            current_streak = 1
            prev_date = completions.first().completion_date.date() # Initialize with the first completion date

            for completion in completions[1:]:
                if completion.completion_date.date() == prev_date + timedelta(days=1):
                    current_streak += 1     
                else:
                    longest_streak = max(longest_streak, current_streak)
                    current_streak = 1                      # Reset streak if there's a gap
                prev_date = completion.completion_date.date()

            return max(longest_streak, current_streak)      # Return the longest streak found
        except Habit.DoesNotExist:
            return 0 
        
    @staticmethod
    def habits_completed_count():
        """
        Returns a tuple with:
        - Total number of unique habits that have at least one (non-deleted) completion
        - Number of those that are still active
        - Number that are now inactive or paused but had completions before

        Returns:
            tuple: (total_completed, active_completed, previously_completed_inactive)
        """
        # Total unique habits with non-deleted completions
        total_completed = Completion.objects.filter(completion_deleted=False)\
            .values("completion_habit_id").distinct().count()

        # Total unique habits with non-deleted completions that are still active
        active_completed = Completion.objects.filter(
            completion_deleted=False,
            completion_habit_id__habit_status="active"
        ).values("completion_habit_id").distinct().count()

        # Previously completed but no longer active (paused/inactive)
        previously_inactive = total_completed - active_completed

        return (total_completed, active_completed, previously_inactive)   


