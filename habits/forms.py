from .models import Habit
from django import forms

# Habit Form
class HabitForm(forms.ModelForm):
  class Meta:
    model = Habit
    fields = ["habit_name", "habit_description", "habit_occurrence", "habit_status"]
