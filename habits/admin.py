from django.contrib import admin
from .models import Habit, Completion

@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ("habit_name", "habit_occurrence", "habit_created_on")
    search_fields = ("habit_name",)

@admin.register(Completion)
class CompletionAdmin(admin.ModelAdmin):
    list_display = ("completion_habit", "completion_date")


