from django.urls import path
from .views import habit_list, habit_detail, mark_completed, create_habit, edit_habit, delete_habit

urlpatterns = [
    path("", habit_list, name="habit_list"),  # Show all habits
    path("create/", create_habit, name="create_habit"), # Create a new habit
    path("<int:habit_id>/", habit_detail, name="habit_detail"),  # View habit details
    path("<int:habit_id>/edit/", edit_habit, name="edit_habit"),  # Edit a habit 
    path("<int:habit_id>/delete/", delete_habit, name="delete_habit"),  # Delete a habit
    path("<int:habit_id>/complete/", mark_completed, name="mark_completed"),  # Mark habit as completed
]
