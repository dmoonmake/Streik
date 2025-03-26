from django.core.management.base import BaseCommand
from habits.models import Habit, Completion
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = "Seed habits with mixed statuses and realistic tracking data matching streaks"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Resetting habits and completions..."))

        Habit.objects.all().delete()
        Completion.objects.all().delete()

        today = datetime.now().date()

        predefined_habits = [
            {"base": "Exercise", "occurrence": "daily", "status": "active"},
            {"base": "Read News", "occurrence": "daily", "status": "paused"},
            {"base": "Meditation", "occurrence": "daily", "status": "inactive"},
            {"base": "Performance Review", "occurrence": "weekly", "status": "active"},
            {"base": "Call Family", "occurrence": "weekly", "status": "paused"},
            {"base": "Clean Garage", "occurrence": "weekly", "status": "inactive"},
            {"base": "Budgeting", "occurrence": "monthly", "status": "active"},
            {"base": "Stretch Goals", "occurrence": "monthly", "status": "paused"},
            {"base": "Donate", "occurrence": "monthly", "status": "inactive"},
        ]

        for habit_def in predefined_habits:
            name = f"{habit_def['base']} ({habit_def['occurrence']})"
            occ = habit_def['occurrence']
            status = habit_def['status']

            # Generate best and last streaks
            best_streak = random.randint(3, 10)
            last_streak = 0 if status == "inactive" else random.randint(1, best_streak)

            habit = Habit.objects.create(
                habit_name=name,
                habit_occurrence=occ,
                habit_status=status,
                habit_best_streak=best_streak,
                habit_last_streak=last_streak
            )

            # Create completions that support the best streak
            if occ == "daily":
                start_best = today - timedelta(days=best_streak + 10)
                for i in range(best_streak):
                    Completion.objects.create(
                        completion_habit_id=habit,
                        completion_date=start_best + timedelta(days=i)
                    )

                # Add recent completions for last streak
                for i in range(last_streak):
                    Completion.objects.create(
                        completion_habit_id=habit,
                        completion_date=today - timedelta(days=i)
                    )

            elif occ == "weekly":
                start_best = today - timedelta(weeks=best_streak + 5)
                for i in range(best_streak):
                    Completion.objects.create(
                        completion_habit_id=habit,
                        completion_date=start_best + timedelta(weeks=i)
                    )

                for i in range(last_streak):
                    Completion.objects.create(
                        completion_habit_id=habit,
                        completion_date=today - timedelta(weeks=i)
                    )

            elif occ == "monthly":
                used_dates = set()

                # Approximate month gap using 30-day steps

                # Best streak months (older)
                for i in range(best_streak):
                    date = today.replace(day=15) - timedelta(days=30 * (best_streak - i + 2))
                    if date not in used_dates:
                        Completion.objects.create(completion_habit_id=habit, completion_date=date)
                        used_dates.add(date)

                # Last streak months (recent)
                for i in range(last_streak):
                    date = today.replace(day=15) - timedelta(days=30 * i)
                    if date not in used_dates:
                        Completion.objects.create(completion_habit_id=habit, completion_date=date)
                        used_dates.add(date)



        self.stdout.write(self.style.SUCCESS("Seeded habits with valid streak completions."))
