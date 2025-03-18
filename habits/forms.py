from django import forms
from .models import Habit

class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ["habit_name", "habit_description", "habit_occurrence"]
