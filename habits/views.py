from .forms import HabitForm
from .models import Habit, Completion, Report
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.safestring import mark_safe
import plotly.graph_objects as go

def analytics_view(request):
  """
  Displays habit analytics, including longest streaks, habit status breakdown, and completion trends.

  Args:
    request (HttpRequest): The HTTP request object.

  Returns:
    HttpResponse: The rendered analytics page.
  """
  habits = Habit.objects.all()
  longest_streak_habits = Report.get_habits_with_longest_streak()
  completion_trend_chart = Report.generate_completion_trend_chart()
  total_completions, active_completions, other_completions = Report.habits_completed_count()

  context = {
    "habits": habits,
    "longest_streak_habits": longest_streak_habits,
    "status_chart_html": Report.generate_status_chart(),
    "streak_chart_html": Report.generate_streak_chart(),
    "completion_trend_chart": completion_trend_chart,
    "total_completions": total_completions, 
    "active_completions": active_completions,
    "other_completions": other_completions,
  }

  return render(request, "habits/analytics.html", context)

def create_habit(request):
  """
  Allows the user to create a new habit using a form.

  Args:
    request (HttpRequest): The HTTP request object.

  Returns:
    HttpResponse: The rendered create habit page or redirects to the habit list page.
  """
  form = HabitForm(request.POST or None)

  if form.is_valid():
    form.save()
    return redirect("habit_list")

  return render(request, "habits/create_habit.html", {"form": form})

def delete_habit(request, habit_id):
  """
  Allows users to delete a habit.

  Args:
    request (HttpRequest): The HTTP request object.
    habit_id (int): The ID of the habit to delete.

  Returns:
    HttpResponse: The rendered delete habit page or redirects to the habit list page.
  """
  habit = get_object_or_404(Habit, habit_id=habit_id)

  if request.method == "POST":
    habit.delete()
    return redirect("habit_list")

  return render(request, "habits/delete_habit.html", {"habit": habit})

def edit_habit(request, habit_id):
  """
  Allows users to edit an existing habit, handling both status and occurrence changes.

  Args:
    request (HttpRequest): The HTTP request object.
    habit_id (int): The ID of the habit to edit.

  Returns:
    HttpResponse: The rendered edit habit page or redirects to the habit detail page.
  """
  habit = get_object_or_404(Habit, habit_id=habit_id)
  current = datetime.now()
  form = HabitForm(request.POST or None, instance=habit)

  old_occurrence = habit.habit_occurrence
  old_status = habit.habit_status

  if form.is_valid():
    updated_habit = form.save(commit=False)
    new_status = form.cleaned_data["habit_status"]
    new_occurrence = form.cleaned_data["habit_occurrence"]

    # === Status change logic ===
    if old_status == "active" and new_status == "paused":
      updated_habit.habit_last_streak = max(habit.habit_last_streak, habit.get_current_streak())

    elif old_status == "paused" and new_status == "active":
      updated_habit.habit_last_streak = max(habit.habit_last_streak, habit.get_current_streak())

    elif new_status == "inactive":
      updated_habit.habit_last_streak = 0
      Completion.objects.filter(completion_habit_id=habit, completion_date=current).update(completion_deleted=True)

    # === Occurrence change logic ===
    if old_occurrence != new_occurrence:
      # When occurrence changes, recalculate streak
      updated_habit.habit_last_streak = updated_habit.get_current_streak()

    updated_habit.save()
    return redirect("habit_detail", habit_id=habit.habit_id)

  return render(request, "habits/edit_habit.html", {"form": form, "habit": habit})


def habit_detail(request, habit_id):
  """
  Display details of a specific habit.

  Args:
    request (HttpRequest): The HTTP request object.
    habit_id (int): The ID of the habit to display.

  Returns:
    HttpResponse: The rendered habit detail page.
  """
  habit = get_object_or_404(Habit, habit_id=habit_id)
  current = datetime.now()
  current_date = current.date()
  completions = Completion.objects.filter(completion_habit_id=habit, completion_deleted=False).order_by("-completion_date")
  latest_completion = completions.first()

  # Generate a bar chart for completion history
  dates = [c.completion_date.strftime("%Y-%m-%d") for c in completions]
  counts = [1] * len(dates)

  fig = go.Figure()
  fig.add_trace(go.Bar(x=dates, y=counts, marker_color="blue"))
  fig.update_layout(
    title=f"Completion History for {habit.habit_name}",
    xaxis_title="Date",
    yaxis_title="Completed",
    yaxis=dict(tickvals=[1], ticktext=["✔"]),
    height=300
  )

  completion_history_chart_html = mark_safe(fig.to_html(include_plotlyjs=False, full_html=False))

  context = {
    "habit": habit,
    "completions": completions,
    "today": current,
    "today_date": current_date,
    "latest_completion": latest_completion,
    "completion_history_chart_html": completion_history_chart_html
  }
  return render(request, "habits/habit_detail.html", context)

def habit_list(request):
  """
  Display a list of all habits with sorting and filtering options.

  Args:
    request (HttpRequest): The HTTP request object.

  Returns:
    HttpResponse: The rendered habit list page.
  """
  habits = Habit.objects.all()
  current_date = datetime.now().date()
  sort_by = request.GET.get("sort_by", "habit_name")
  filter_by_occurrence = request.GET.get("filter_by_occurrence", "all")
  filter_by_status = request.GET.get("filter_by_status", "active")  # Default to active

  # Handle sorting
  if filter_by_occurrence in ["daily", "weekly", "monthly"]:
    habits = habits.filter(habit_occurrence=filter_by_occurrence)

  if filter_by_status in ["active", "paused", "inactive"]:
    habits = habits.filter(habit_status=filter_by_status)

  if sort_by == "streak":
    habits = habits.order_by("-habit_best_streak")
  else:
    habits = habits.order_by(sort_by)

  current = datetime.now()
  context = {
    "habits": habits,
    "today": current,
    "sort_by": sort_by,
    "filter_by_occurrence": filter_by_occurrence,
    "filter_by_status": filter_by_status,
    "today_date": current_date
  }
  return render(request, "habits/habit_list.html", context)

def mark_completed(request, habit_id):
  """
  Marks a habit as completed for today.

  Args:
    request (HttpRequest): The HTTP request object.
    habit_id (int): The ID of the habit to mark as completed.

  Returns:
    HttpResponse: Redirects to the habit detail page.
  """
  habit = get_object_or_404(Habit, habit_id=habit_id)
  current = datetime.now()

  completion, created = Completion.objects.get_or_create(completion_habit_id=habit, completion_date=current)
  
  # If the completion already exists and is marked as deleted, restore it
  if not created and completion.completion_deleted:
    completion.completion_deleted = False
    completion.save()

  # Update streak immediately after new completion
  habit.get_current_streak()

  return redirect("habit_detail", habit_id=habit_id)



