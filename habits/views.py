from django.shortcuts import render, redirect, get_object_or_404
from .models import Habit, Completion
from datetime import date, timedelta
from django.db.models import Count, Avg
from .forms import HabitForm
from django.db.models import Max 
from django.utils.safestring import mark_safe

import plotly.graph_objects as go

# def habit_list(request):
#     """
#     Display a list of all habits.
#     """
#     habits = Habit.objects.prefetch_related("completions").all()
#     today = date.today()
#     return render(request, "habits/habit_list.html", {"habits": habits, "today": today})

def habit_list(request):
    """
    View for listing habits.
    """
    habits = Habit.objects.all().prefetch_related("completions")
    today = date.today()  # ✅ Ensure today's date is available in the template

   # Attach latest completion to each habit
    for habit in habits:
        latest = habit.completions.filter(completion_deleted=False).order_by("-completion_date").first()
        habit.latest_completion = latest.completion_date if latest else None
        habit.latest_completion_deleted = latest.completion_deleted if latest else False

    context = {
        "habits": habits,
        "today": today,  # ✅ Pass today into the template for date comparison
        "latest_completion": latest_completion
    }

    return render(request, "habits/habit_list.html", context)

def habit_detail(request, habit_id):
    """
    Display details of a specific habit.
    """
    habit = get_object_or_404(Habit, habit_id=habit_id)
    today = date.today()
    completions = Completion.objects.filter(completion_habit_id=habit).order_by("-completion_date")
    latest_completion = completions.first()

    # ✅ Prepare data for Plotly
    dates = [c.completion_date.strftime("%Y-%m-%d") for c in completions]
    counts = [1] * len(dates)  # Just mark 1 per completion

    # ✅ Create Plotly chart
    fig = go.Figure()
    fig.add_trace(go.Bar(x=dates, y=counts, marker_color="blue"))
    fig.update_layout(
        title=f"Completion History for {habit.habit_name}",
        xaxis_title="Date",
        yaxis_title="Completed",
        yaxis=dict(tickvals=[1], ticktext=["✔"]),
        height=300
    )

    chart_html = mark_safe(fig.to_html(include_plotlyjs=False, full_html=False))

    return render(request, "habits/habit_detail.html", {"habit": habit, "completions": completions, "today": today, "latest_completion": latest_completion, "chart_html": chart_html})

def mark_completed(request, habit_id):
    """
    Marks a habit as completed for today.
    """
    habit = get_object_or_404(Habit, habit_id=habit_id)
    today = date.today()

    # Check if a completion exists for today
    completion = Completion.objects.filter(completion_habit_id=habit, completion_date=today).first()

    if completion:
        if completion.completion_deleted:
            # ✅ Reactivate the deleted completion instead of blocking
            completion.completion_deleted = False
            completion.save()
    else:
        # ✅ Create a new completion if none exists
        Completion.objects.create(completion_habit_id=habit, completion_date=today)

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
    Allows users to edit an existing habit, updating the streak correctly based on status changes.
    """
    habit = get_object_or_404(Habit, habit_id=habit_id)
    today = date.today()

    if request.method == "POST":
        form = HabitForm(request.POST, instance=habit)
        if form.is_valid():
            new_status = form.cleaned_data["habit_status"]

            # Store last streak before pausing
            if habit.habit_status == "active" and new_status == "paused":
                habit.habit_last_streak = max(habit.habit_last_streak, habit.get_current_streak())

            # Restore last streak when reactivating a paused habit
            elif habit.habit_status == "paused" and new_status == "active":
                habit.habit_last_streak = max(habit.habit_last_streak, habit.get_current_streak())

            # Reset streak when inactivating a habit
            elif new_status == "inactive":
                habit.habit_last_streak = 0 # Reset streak
                Completion.objects.filter(completion_habit_id=habit, completion_date=today).update(completion_deleted=True)  # Mark as deleted instead of removing


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



    # Filter completions by date range
    time_filter = request.GET.get("time_filter", "all")
    today = date.today()

    if time_filter == "last_7_days":
        date_range = today - timedelta(days=7)
    elif time_filter == "last_30_days":
        date_range = today - timedelta(days=30)
    else:
        date_range = None  # No filter

    # Get all completions
    completions = Completion.objects.all()
    if date_range:
        completions = completions.filter(completion_date__gte=date_range)

    # Identify the habit with the longest streak
    top_habit = max(habits, key=lambda h: h.habit_best_streak, default=None)

    # Ensure `max_streak` is not None
    max_streak = habits.aggregate(max_streak=Max("habit_best_streak"))["max_streak"]

    # Retrieve all habits with the max streak
    longest_streak_habits = habits.filter(habit_best_streak=max_streak) if max_streak is not None else []

    context = {
        "longest_streak_habits": longest_streak_habits,
    }

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

    # # Total completed habits
    # total_completed = completions.count()

    # ✅ Count all completed habits (including soft-deleted ones)
    total_completed_habits = Completion.objects.filter(completion_deleted=False).values("completion_habit_id").distinct().count()

    # ✅ Count active completed habits
    active_completed_habits = Completion.objects.filter(completion_habit_id__habit_status="active", completion_deleted=False).values("completion_habit_id").distinct().count()

    # ✅ Count inactive completed habits (previously completed but now inactive)
    inactive_completed_habits = total_completed_habits - active_completed_habits

    # # Most completed habit
    # most_completed_habit = completions.values("completion_habit_id__habit_name").annotate(
    #     count=Count("completion_habit_id")
    # ).order_by("-count").first()

    # Average streak length
    average_streak = Habit.objects.aggregate(avg_streak=Avg("habit_best_streak"))["avg_streak"] or 0

    # Completion trends over time
    trend_data = completions.values("completion_date").annotate(count=Count("completion_id")).order_by("completion_date")

    dates = [item["completion_date"] for item in trend_data]
    counts = [item["count"] for item in trend_data]

    # Generate Completion Trend Chart and convert dates to YYYY-MM-DD format (removing time)
    dates = [date.strftime("%d-%m-%Y") for date in dates]  # Convert to string format

    # Generate Completion Trend Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=counts, mode="lines+markers", name="Completions"))
    fig.update_layout(title="Habit Completion Trends", xaxis_title="Date", yaxis_title="Completions")


    completion_trend_chart = fig.to_html(full_html=False)

    # context = {
    #     "total_completed": total_completed,
    #     # "most_completed_habit": most_completed_habit,
    #     "average_streak": round(average_streak, 2),
    #     "completion_trend_chart": completion_trend_chart,
    #     "time_filter": time_filter,
    # }

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
        # "total_completed": total_completed,
        # "most_completed_habit": most_completed_habit,
        "total_completed_habits": total_completed_habits,
        "active_completed_habits": active_completed_habits,
        "inactive_completed_habits": inactive_completed_habits,
        "average_streak": round(average_streak, 2),
        "completion_trend_chart": completion_trend_chart,
        "time_filter": time_filter,
        "longest_streak_habits": longest_streak_habits,
    }

    return render(request, "habits/analytics.html", context)