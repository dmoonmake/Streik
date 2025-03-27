from .models import Habit, Completion
from django.contrib import admin

# Add Completion model to the admin panel
@admin.register(Completion)             
class CompletionAdmin(admin.ModelAdmin):
  list_display = ("completion_habit_id", "completion_date", "completion_deleted")

# Add Habit model to the admin panel
@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
  list_display = ("habit_name", "habit_occurrence", "habit_created_on", "habit_status")
  search_fields = ("habit_name",)








