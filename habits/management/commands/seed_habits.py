from django.core.management.base import BaseCommand
from habits.models import Habit, Completion
from datetime import datetime

class Command(BaseCommand):
  help = "Seed habits with predefined completions and streaks from spreadsheet data."

  def handle(self, *args, **kwargs):
    self.stdout.write(self.style.NOTICE("Resetting habits and completions..."))

    # Delete only habits that match your seed pattern
    seeded_habits = Habit.objects.filter(habit_name__icontains="(")
    Completion.objects.filter(completion_habit_id__in=seeded_habits).delete()
    seeded_habits.delete()

    def parse(d):  # Return naive datetime (compatible with USE_TZ = False)
      return datetime.strptime(d, "%d/%m/%Y")
    habits_data = [
      {
        "name": "Exercise",
        "occurrence": "daily",
        "status": "active",
        "dates": [
          "12/02/2025", "13/02/2025", "14/02/2025", "15/02/2025",
          "18/02/2025", "19/02/2025", "20/02/2025", "21/02/2025", "22/02/2025",
          "12/03/2025", "15/03/2025"
        ],
        "last": 0,
        "best": 5
      },
      {
        "name": "Read News",
        "occurrence": "daily",
        "status": "paused",
        "dates": [
          "18/02/2025", "19/02/2025", "20/02/2025",
          "12/03/2025", "13/03/2025", "14/03/2025", "15/03/2025", "16/03/2025",
          "24/03/2025", "25/03/2025", "26/03/2025"
        ],
        "last": 3,
        "best": 5
      },
      {
        "name": "Meditation",
        "occurrence": "daily",
        "status": "inactive",
        "dates": [
          "21/02/2025", "22/02/2025", "23/02/2025", "24/02/2025", "25/02/2025", "26/02/2025", "27/02/2025", "28/02/2025",
          "23/03/2025", "24/03/2025", "25/03/2025", "26/03/2025"
        ],
        "last": 0,
        "best": 8
      },
      {
        "name": "Date Night",
        "occurrence": "weekly",
        "status": "active",
        "dates": ["20/02/2025", "27/02/2025", "06/03/2025", "13/03/2025", "20/03/2025", "23/03/2025"],
        "last": 5,
        "best": 5
      },
      {
        "name": "Call Family",
        "occurrence": "weekly",
        "status": "paused",
        "dates": [
          "12/02/2025", "15/02/2025", "18/02/2025", "21/02/2025", "24/02/2025", "27/02/2025",
          "02/03/2025", "05/03/2025", "23/03/2025", "24/03/2025", "25/03/2025"],
        "last": 1,
        "best": 3
      },
      {
        "name": "Washing",
        "occurrence": "weekly",
        "status": "inactive",
        "dates": ["12/02/2025", "15/02/2025", "18/02/2025", "21/02/2025", "24/02/2025", "27/02/2025",
                  "02/03/2025", "05/03/2025"],
        "last": 0,
        "best": 3
      },
      {
        "name": "Budget Review",
        "occurrence": "monthly",
        "status": "active",
        "dates": ["01/01/2025", "31/01/2025", "02/02/2025", "04/03/2025", "25/03/2025"],
        "last": 3,
        "best": 3
      },
      {
        "name": "Stretch Goals",
        "occurrence": "monthly",
        "status": "paused",
        "dates": ["01/01/2025", "02/02/2025"],
        "last": 0,
        "best": 2
      },
      {
        "name": "Charity Shop",
        "occurrence": "monthly",
        "status": "inactive",
        "dates": ["01/01/2025", "31/01/2025", "02/02/2025", "04/03/2025", "25/03/2025"],
        "last": 0,
        "best": 3
      }
    ]

    for h in habits_data:
      habit = Habit.objects.create(
        habit_name=h["name"],
        habit_occurrence=h["occurrence"],
        habit_status=h["status"],
        habit_last_streak=h["last"],
        habit_best_streak=h["best"]
      )
      for d in h["dates"]:
        Completion.objects.create(
          completion_habit_id=habit,
          completion_date=parse(d)
        )

    self.stdout.write(self.style.SUCCESS("Habit seeds loaded exactly as specified."))

