from django.shortcuts import render, redirect, get_object_or_404
from .models import Habit, Completion
from datetime import date
from .forms import HabitForm

import plotly.graph_objects as go

def habit_list(request):
    """
    Display a list of all habits.
    """
    habits = Habit.objects.all()
    return render(request, "habits/habit_list.html", {"habits": habits})


def habit_detail(request, habit_id):
    """
    Display details of a specific habit.
    """
    habit = get_object_or_404(Habit, habit_id=habit_id)
    completions = Completion.objects.filter(completion_habit=habit).order_by("-completion_date")
    return render(request, "habits/habit_detail.html", {"habit": habit, "completions": completions})


def mark_completed(request, habit_id):
    """
    Marks a habit as completed for today.
    """
    habit = get_object_or_404(Habit, habit_id=habit_id)
    today = date.today()

    # Check if the habit is already completed today
    if not Completion.objects.filter(completion_habit=habit, completion_date=today).exists():
        Completion.objects.create(completion_habit=habit, completion_date=today)

    return redirect("habit_detail", habit_id=habit_id)

def create_habit(request):
    """
    Allows the user to create a new habit using a form.
    """
    if request.method == "POST":
        form = HabitForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("habit_list")
    else:
        form = HabitForm()

    return render(request, "habits/create_habit.html", {"form": form})

def edit_habit(request, habit_id):
    """
    Allows users to edit an existing habit.
    """
    habit = get_object_or_404(Habit, habit_id=habit_id)

    if request.method == "POST":
        form = HabitForm(request.POST, instance=habit)
        if form.is_valid():
            form.save()
            return redirect("habit_detail", habit_id=habit.habit_id)
    else:
        form = HabitForm(instance=habit)

    return render(request, "habits/edit_habit.html", {"form": form, "habit": habit})


def delete_habit(request, habit_id):
    """
    Allows users to delete a habit.
    """
    habit = get_object_or_404(Habit, habit_id=habit_id)
    
    if request.method == "POST":
        habit.delete()
        return redirect("habit_list")

    return render(request, "habits/delete_habit.html", {"habit": habit})

def habit_list(request):
    """
    Display a list of all habits with sorting and filtering options.
    """

    habits = Habit.objects.all()
    
    sort_by = request.GET.get("sort_by", "habit_name")  # Default: sort by name
    # Get filter values from the request
    occurrence_filter = request.GET.get("filter_by_occurrence", "all")
    status_filter = request.GET.get("filter_by_status", "all")

    # Apply filters
    if occurrence_filter in ["daily", "weekly", "monthly"]:
        habits = habits.filter(habit_occurrence=occurrence_filter)

    if status_filter in ["active", "paused", "inactive"]:
        habits = habits.filter(habit_status=status_filter)

    # Apply sorting
    if sort_by == "streak":
        habits = sorted(habits, key=lambda h: h.get_current_streak(), reverse=True)
    else:
        habits = habits.order_by(sort_by)

    return render(request, "habits/habit_list.html", {
        "habits": habits,
        "sort_by": sort_by,
        "filter_by_occurrence": occurrence_filter,
        "filter_by_status": status_filter,
    })

def generate_status_chart():
    """Generate a Plotly Pie Chart for Habit Statuses."""
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

def generate_streak_chart():
    """Generate a Plotly Bar Chart for Habit Streaks."""
    habits = Habit.objects.all().order_by("-habit_best_streak")[:5]  # Top 5 habits by best streak

    habit_names = [habit.habit_name for habit in habits]
    best_streaks = [habit.habit_best_streak for habit in habits]
    current_streaks = [habit.get_current_streak() for habit in habits]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=habit_names, y=best_streaks,
        name="Best Streak", marker_color="#007BFF"
    ))

    fig.add_trace(go.Bar(
        x=habit_names, y=current_streaks,
        name="Current Streak", marker_color="#34A853"
    ))

    fig.update_layout(
        title="Habit Streak Trends",
        xaxis_title="Habits",
        yaxis_title="Number of Days",
        barmode="group"
    )

    return fig.to_html(full_html=False)

def analytics_view(request):
    """
    Display analytics for habits, including the longest streak, habit status breakdown,
    filtering by occurrence, and embedded Plotly graphs.
    """
    # Get all habits
    habits = Habit.objects.all()

    # Identify the habit with the longest streak
    top_habit = max(habits, key=lambda h: h.habit_best_streak, default=None)

    # Count habits by status
    active_count = habits.filter(habit_status="active").count()
    paused_count = habits.filter(habit_status="paused").count()
    inactive_count = habits.filter(habit_status="inactive").count()

    sort_by = request.GET.get("sort_by", "habit_name")  # Default: sort by name
    # Get filter values from the request
    occurrence_filter = request.GET.get("filter_by_occurrence", "all")
    status_filter = request.GET.get("filter_by_status", "all")

    # Apply filters
    if occurrence_filter in ["daily", "weekly", "monthly"]:
        habits = habits.filter(habit_occurrence=occurrence_filter)

    if status_filter in ["active", "paused", "inactive"]:
        habits = habits.filter(habit_status=status_filter)

    # Apply sorting
    if sort_by == "streak":
        habits = sorted(habits, key=lambda h: h.get_current_streak(), reverse=True)
    else:
        habits = habits.order_by(sort_by)

    # Generate Plotly charts
    status_chart_html = generate_status_chart()
    streak_chart_html = generate_streak_chart()

    context = {
        "habits": habits,
        "top_habit": top_habit,
        "active_count": active_count,
        "paused_count": paused_count,
        "inactive_count": inactive_count,
        "filter_by": occurrence_filter,
        "status_chart_html": status_chart_html,
        "streak_chart_html": streak_chart_html,
    }

    return render(request, "habits/analytics.html", context)