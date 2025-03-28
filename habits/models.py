

from django.db import models
from django.db.models import Max
import plotly.graph_objects as go
from collections import Counter
from datetime import timedelta, datetime

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

	def _calculate_daily_streak(self, completions):
		"""
		Calculate the current streak for a daily habit.

		Args:
			completions (QuerySet): The list of completions for the habit. 

		Returns:
			int: The current streak count.
		"""
		# Get the last completion date
		today = datetime.now().date()

		 # Only consider completions in the past or today, and not soft-deleted
		valid_dates = (
			[c.completion_date.date() 
			for c in completions 
			if not c.completion_deleted and c.completion_date.date() <= today])

		streak = 0

		if today not in valid_dates:  # No completion today
			current = today - timedelta(days=1) # Start from yesterday
		else:
			current = today  # Start from today

		while current in valid_dates:  # Count backwards
			streak += 1
			current -= timedelta(days=1)
		
		self._update_streaks(streak)
		return streak  

	def _calculate_monthly_streak(self, completions):
		"""
		Calculates monthly streak (one completion per calendar month).

		Args:
			completions (QuerySet): The list of completions for the habit.

		Returns:
			int: The current streak count.
		"""
		if not completions:
			return 0

		# Get all completion months
		months = []
		for c in completions:
			months.append((c.completion_date.year, c.completion_date.month))

		# Remove duplicate completions in same month
		unique_months = list(dict.fromkeys(months))
		streak = 1

		for i in range(1, len(unique_months)):  # Start from 2nd completion
			prev_year, prev_month = unique_months[i - 1]  # Previous completion
			curr_year, curr_month = unique_months[i]  # Current completion

			# Check if month is consecutive
			if (curr_year == prev_year and curr_month == prev_month + 1) or \
			(curr_year == prev_year + 1 and prev_month == 12 and curr_month == 1):
				streak += 1
			else:
				streak = 1  # streak broken

		self._update_streaks(streak)
		return streak

	def get_best_streak(self):
		"""
		Recalculate and return the best streak based on all completions.

		Returns:
			int: The best streak ever.
		"""
		completions = self.completions.filter(completion_deleted=False).order_by("completion_date")

		if not completions:
			return 0

		if self.habit_occurrence == "daily":
			dates = sorted([c.completion_date.date() for c in completions if not c.completion_deleted ])  # Sort by date, excluded the deleted completions
			best = streak = 1

			for i in range(1, len(dates)):
				if dates[i] == dates[i - 1] + timedelta(days=1):  # Check for consecutive days
					streak += 1
					best = max(best, streak)  # Update best streak
				else:
					streak = 1
			return best

		elif self.habit_occurrence == "weekly":
			weeks = [(c.completion_date.isocalendar()[:2]) for c in completions if not c.completion_deleted]	# sort by week, excluded the deleted completions
			unique_weeks = list(dict.fromkeys(weeks))  # Remove duplicates
			best = streak = 1

			for i in range(1, len(unique_weeks)):  # Start from 2nd completion
				prev_year, prev_week = unique_weeks[i - 1]
				curr_year, curr_week = unique_weeks[i]
				
				# Check if week is consecutive
				is_consecutive = (
					(curr_year == prev_year and curr_week == prev_week + 1) or
					(curr_year == prev_year + 1 and prev_week == 52 and curr_week == 1)
				)

				if is_consecutive:
					streak += 1
					best = max(best, streak)
				else:
					streak = 1
			return best

		elif self.habit_occurrence == "monthly":
			months = [(c.completion_date.year, c.completion_date.month) for c in completions if not c.completion_deleted] # sort by month, excluded the deleted completions
			unique_months = list(dict.fromkeys(months))
			best = streak = 1

			for i in range(1, len(unique_months)):  # Start from 2nd completion
				prev_y, prev_m = unique_months[i - 1]
				curr_y, curr_m = unique_months[i]

				# Check if month is consecutive
				is_consecutive = (
					(curr_y == prev_y and curr_m == prev_m + 1) or
					(curr_y == prev_y + 1 and prev_m == 12 and curr_m == 1)
				)

				if is_consecutive:
					streak += 1
					best = max(best, streak)
				else:
					streak = 1
			return best

		return 0

	def _calculate_weekly_streak(self, completions):
		"""
		Calculates current streak of weekly completions starting on Mondays.

		Args:
			completions (QuerySet): The list of completions for the habit.

		Returns:
			int: The current streak count.
		"""
		if not completions:
			return 0

		streak = 1
		weeks = sorted([c.completion_date.isocalendar()[:2] for c in completions if not c.completion_deleted])  # sort by week, excluded the deleted completions

		for i in range(len(weeks) - 1):
			year1, week1 = weeks[i]
			year2, week2 = weeks[i + 1]

			# Check for consecutive ISO weeks
			if (year2 == year1 and week2 == week1 + 1) or (year2 == year1 + 1 and week1 == 52 and week2 == 1):
				streak += 1
			else:
				streak = 1

		self._update_streaks(streak)
		return streak

	def _update_streaks(self, current_streak):
		"""
		Update the habit's last streak and best streak by recalculation.

		Args:
			current_streak (int): The latest streak based on current completions.

		Updates:
			habit_last_streak (int): The latest streak.
			habit_best_streak (int): The best streak.
		"""
		self.habit_last_streak = current_streak
		self.habit_best_streak = self.get_best_streak()
		self.save(update_fields=["habit_last_streak", "habit_best_streak"])


	def get_current_streak(self):
		"""
		Calculates the current streak based on the habit's status and occurrence:

		- If habit is inactive, return 0.
		- If habit is paused, return the last streak before pausing.
		- If habit is active, calculate streak using the occurrence cycle:
			- daily: at midnight
			- weekly: at the ISO week start (Monday)
			- monthly: at the 1st of each month

		Returns:
			int: The current streak count.
		"""
		if self.habit_status == "inactive":  # Habit is not being tracked
			self.habit_last_streak = 0
			self.save(update_fields=["habit_last_streak"])
			return 0

		if self.habit_status == "paused":  # Habit is paused
			return self.habit_last_streak

		completions = list(
			self.completions.filter(completion_deleted=False).order_by("completion_date")
		)

		# Calculate streak based on occurrence
		if self.habit_occurrence == "daily":
			streak = self._calculate_daily_streak(completions)
		elif self.habit_occurrence == "weekly":
			streak = self._calculate_weekly_streak(completions)
		elif self.habit_occurrence == "monthly":
			streak = self._calculate_monthly_streak(completions)
		else:
			streak = 0

		# Update best streak if current streak is higher
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
		filter_habits_by_occurrence(occurrence: str) -> QuerySet:
			Filters habits by their occurrence type (daily, weekly, monthly).

		generate_completion_chart(completions, habit_name, habit_occurrence) -> str:
			Generates a dynamic Plotly bar chart for a habit's completion history.

		generate_completion_trend_chart() -> str:
			Generates a Plotly Line Chart for Completion Trends Over Time.

		generate_status_chart() -> str:
			Generates a Plotly Pie Chart for Habit Statuses.

		generate_streak_chart() -> str:
			Generates a Plotly Bar Chart for Habit Streaks.

		get_habits_with_longest_streak() -> QuerySet:
			Finds all habits that currently have the longest streak.

		get_longest_streak(habit_id: int) -> int:
			Calculates the longest consecutive streak of completions for a given habit.
		habits_completed_count() -> tuple:
			Returns a tuple with:
			- Total number of completions (non-deleted)
			- Number of completions linked to active habits
			- Number of completions linked to paused or inactive habits
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
	def generate_completion_chart(completions, habit_name, habit_occurrence):
		"""
		Generates a dynamic Plotly bar chart for a habit's completion history for details page.

		Args:
			completions (QuerySet): The list of completions for the habit.
			habit_name (str): The name of the habit.
			habit_occurrence (str): One of 'daily', 'weekly', 'monthly'.

		Returns:
			str: HTML representation of the chart.
		"""

		# Group dates depending on frequency
		if habit_occurrence == "daily":
			grouped = [c.completion_date.date().strftime("%Y-%m-%d") for c in completions if not c.completion_deleted]

		elif habit_occurrence == "weekly":
			grouped = [c.completion_date.date().strftime("Week %W, %Y") for c in completions if not c.completion_deleted]

		elif habit_occurrence == "monthly":
			grouped = [c.completion_date.date().strftime("%B %Y") for c in completions if not c.completion_deleted]

		else:
			grouped = [c.completion_date.date().strftime("%Y-%m-%d") for c in completions if not c.completion_deleted]

		counts = Counter(grouped)
		x = list(counts.keys())
		y = list(counts.values())

		fig = go.Figure()
		fig.add_trace(go.Bar(x=x, y=y, marker_color="blue"))

		# Update layout based on occurrence
		fig.update_layout(
			title=f"Completion History for {habit_name}",
			xaxis_title="Period",
			yaxis_title="Completions",
			height=300,
			yaxis=dict(tickvals=[1], ticktext=["✔"]) if habit_occurrence in ["daily", "weekly", "monthly"] else None
		)
		
		return fig.to_html(full_html=False)
	
	@staticmethod
	def generate_completion_trend_chart():
		"""
		Generate a Plotly Line Chart for Completion Trends Over Time.

		Returns:
			str: The HTML representation of the chart.
		"""
		# Group completions by date and count
		completions = Completion.objects.filter(completion_deleted=False).values("completion_date").annotate(
			count=models.Count("completion_id")
		).order_by("completion_date")

		# Extract dates and counts
		dates = [item["completion_date"].strftime("%Y-%m-%d") for item in completions]
		counts = [item["count"] for item in completions]

		# Create the Plotly chart
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
		# Count habits by status
		habits = Habit.objects.all()
		status_counts = {
			"Active": habits.filter(habit_status="active").count(),
			"Paused": habits.filter(habit_status="paused").count(),
			"Inactive": habits.filter(habit_status="inactive").count(),
		}

		# Create the Plotly chart
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
		# Get top 5 habits by best streak
		habits = Habit.objects.all().order_by("-habit_best_streak")[:5]  # Top 5 habits by streak

		# Create the Plotly chart
		fig = go.Figure()
		fig.add_trace(go.Bar(
			x=[habit.habit_name for habit in habits], 
			y=[habit.habit_best_streak for habit in habits],
			name="Best Streak", marker_color="#007BFF"
		))

		# Add current streaks
		fig.add_trace(go.Bar(
			x=[habit.habit_name for habit in habits], 
			y=[habit.get_current_streak() for habit in habits],
			name="Current Streak", marker_color="#34A853"
		))

		# Update layout
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
		# Get the maximum streak value
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
			
			# Calculate the longest streak
			longest_streak = 1
			current_streak = 1
			prev_date = completions.first().completion_date.date() # Initialize with the first completion date

			# Iterate over completions to find the longest streak
			for completion in completions[1:]:
				if completion.completion_date.date() == prev_date + timedelta(days=1):
					current_streak += 1     
				else:
					longest_streak = max(longest_streak, current_streak)
					current_streak = 1                      # Reset streak if there's a gap
				prev_date = completion.completion_date.date()

			return max(longest_streak, current_streak)      # Return the longest streak found
		
		# Handle Habit.DoesNotExist exception
		except Habit.DoesNotExist:
			return 0 
        

	@staticmethod
	def habits_completed_count():
		"""
		Returns a tuple with:
		- Total number of completions (non-deleted)
		- Number of completions linked to active habits
		- Number of completions linked to paused or inactive habits

		Returns:
			tuple: (total_completions, active_completions, other_completions)
		"""
		# All non-deleted completions
		total_completions = Completion.objects.filter(completion_deleted=False).count()

		# Non-deleted completions where the habit is active
		active_completions = Completion.objects.filter(
			completion_deleted=False,
			completion_habit_id__habit_status="active"
		).count()

		# All others (paused or inactive)
		other_completions  = total_completions - active_completions

		return (total_completions, active_completions, other_completions)



