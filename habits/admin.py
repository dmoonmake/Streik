from .models import Habit, Completion
from django.contrib import admin

@admin.register(Completion)             
class CompletionAdmin(admin.ModelAdmin):
    list_display = ("completion_habit_id", "completion_date")

@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ("habit_name", "habit_occurrence", "habit_created_on")
    search_fields = ("habit_name",)




