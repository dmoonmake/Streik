from django.shortcuts import render, redirect, get_object_or_404
from .models import Habit, Completion
from datetime import date
from .forms import HabitForm

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
    sort_by = request.GET.get("sort_by", "habit_name")  # Default: sort by name
    filter_by = request.GET.get("filter_by", "all")  # Default: show all

    habits = Habit.objects.all()

    # Apply filtering based on occurrence
    if filter_by in ["daily", "weekly", "monthly"]:
        habits = habits.filter(habit_occurrence=filter_by)

    # Apply sorting
    if sort_by == "streak":
        habits = sorted(habits, key=lambda h: h.get_current_streak(), reverse=True)
    else:
        habits = habits.order_by(sort_by)

    return render(request, "habits/habit_list.html", {
        "habits": habits,
        "sort_by": sort_by,
        "filter_by": filter_by
    })

