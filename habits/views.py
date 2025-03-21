from django.shortcuts import render, redirect, get_object_or_404
from .models import Habit, Completion, Report
from datetime import date
from .forms import HabitForm
from django.utils.safestring import mark_safe
import plotly.graph_objects as go

### HABIT VIEWS ###

def habit_list(request):
    """
    Displays a list of all habits with sorting and filtering options.
    """
    habits = Habit.objects.prefetch_related("completions").all()
    today = date.today()

    # Filtering
    occurrence_filter = request.GET.get("filter_by_occurrence", "all")
    status_filter = request.GET.get("filter_by_status", "active")
    sort_by = request.GET.get("sort_by", "habit_name")  # Default sorting

    if occurrence_filter in ["daily", "weekly", "monthly"]:
        habits = habits.filter(habit_occurrence=occurrence_filter)

    if status_filter in ["active", "paused", "inactive"]:
        habits = habits.filter(habit_status=status_filter)

    # Sorting
    if sort_by == "streak":
        habits = sorted(habits, key=lambda h: h.get_current_streak(), reverse=True)
    else:
        habits = habits.order_by(sort_by)

    return render(request, "habits/habit_list.html", {
        "habits": habits,
        "today": today,
        "sort_by": sort_by,
        "filter_by_occurrence": occurrence_filter,
        "filter_by_status": status_filter,
    })

def habit_detail(request, habit_id):
    """
    Displays the details of a specific habit.
    """
    habit = get_object_or_404(Habit, habit_id=habit_id)
    today = date.today()
    completions = habit.completions.filter(completion_deleted=False).order_by("-completion_date")
    latest_completion = completions.first()

    # Generate Completion History Chart
    chart_html = Report.generate_completion_chart(completions, habit.habit_name)

    return render(request, "habits/habit_detail.html", {
        "habit": habit,
        "completions": completions,
        "today": today,
        "latest_completion": latest_completion,
        "chart_html": chart_html,
    })

def mark_completed(request, habit_id):
    """
    Marks a habit as completed for today.
    """
    habit = get_object_or_404(Habit, habit_id=habit_id)
    today = date.today()

    completion, created = Completion.objects.get_or_create(completion_habit_id=habit, completion_date=today)
    
    if not created and completion.completion_deleted:
        completion.completion_deleted = False
        completion.save()

    # Update streak immediately after new completion
    habit.get_current_streak()

    return redirect("habit_detail", habit_id=habit_id)


def create_habit(request):
    """
    Allows the user to create a new habit using a form.
    """
    form = HabitForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect("habit_list")

    return render(request, "habits/create_habit.html", {"form": form})


def edit_habit(request, habit_id):
    """
    Allows users to edit an existing habit while handling status changes properly.
    """
    habit = get_object_or_404(Habit, habit_id=habit_id)
    today = date.today()
    form = HabitForm(request.POST or None, instance=habit)

    if form.is_valid():
        new_status = form.cleaned_data["habit_status"]

        if habit.habit_status == "active" and new_status == "paused":
            habit.habit_last_streak = max(habit.habit_last_streak, habit.get_current_streak())

        elif habit.habit_status == "paused" and new_status == "active":
            habit.habit_last_streak = max(habit.habit_last_streak, habit.get_current_streak())

        elif new_status == "inactive":
            habit.habit_last_streak = 0
            Completion.objects.filter(completion_habit_id=habit, completion_date=today).update(completion_deleted=True)

        form.save()
        return redirect("habit_detail", habit_id=habit.habit_id)

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


### ANALYTICS & REPORTING VIEWS ###

def analytics_view(request):
    """
    Displays habit analytics, including longest streaks, habit status breakdown, and completion trends.
    """
    habits = Habit.objects.all()
    longest_streak_habits = Report.get_habits_with_longest_streak()
    completion_trend_chart = Report.generate_completion_trend_chart()

    context = {
        "habits": habits,
        "longest_streak_habits": longest_streak_habits,
        "status_chart_html": Report.generate_status_chart(),
        "streak_chart_html": Report.generate_streak_chart(),
        "completion_trend_chart": completion_trend_chart,
    }

    return render(request, "habits/analytics.html", context)
