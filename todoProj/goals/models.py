from django.conf import settings #to Access the setting.AUTH_USER_MODEL → the User model in your project (for user = models.ForeignKey(...))
from django.db import models     #ORM Tools
from django.utils import timezone    #now()function
from django.core.exceptions import ValidationError #Lets you raise an error when data is invalid.
import logging  #Python’s built-in logging module for recording system events.
from django.db.models.signals import post_save # run code auto when certain actions happen post_save()
from django.dispatch import receiver     #decorator connects a function to a signal.

logger = logging.getLogger(__name__)

class Goal(models.Model): #Defines a database table called Goal.
    #Each instance = one row in the table.
    class Status(models.TextChoices):#Inner Enum for Choices
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        DONE = "done", "Done"
    
    user = models.ForeignKey(     #this from settings.py + 
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="goals",
        db_index=True,
        null=True, # super Important ## they make the $$<python manage.py makemigrations> work Effectively
        blank=True, # super Important ## they make the $$<python manage.py makemigrations> work Effectively
    )
    #each field = one column inthe table  
    title = models.CharField(max_length=200) 
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,                   # frequent filter/sort target
    )
    deadline = models.DateField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Note: ordering by a nullable field can be surprising (DB-dependent null placement)
        ordering = ["status", "deadline", "-created_at"]
        # Remove if duplicates should be allowed.
        constraints = [
            models.CheckConstraint(
                check=~models.Q(title=""), #make sure the title is not empty
                name="goal_title_not_empty",
            ),
            models.UniqueConstraint(
                fields=["user", "title"], 
                name="unique_goal_title_per_user"),
        ]

    def clean(self):
        """
        Validates that the deadline is not in the past.
        This check is enforced both when creating and editing a Goal instance.
        """
        # disallow deadlines in the past for *new* or edited goals
        if self.deadline and self.deadline < timezone.now().date():
            raise ValidationError({"deadline": "Deadline cannot be in the past."})

    def __str__(self):#Defines how the object looks in the admin or shell → shows the goal’s title.
        return self.title


class Task(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tasks",
        db_index=True,
        null=True, # super Important ## they make the $$<python manage.py makemigrations> work Effectively
        blank=True,
    )
    #Connects each task to its parent Goal
    goal = models.ForeignKey(
        Goal,
        on_delete=models.CASCADE,
        related_name="tasks",#allows goal.tasks.all() to list all tasks under that goal.
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True, db_index=True)
    is_done = models.BooleanField(default=False, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # You had ascending created_at; often descending is nicer in UIs—keep yours if you prefer.
        ordering = ["is_done", "due_date", "-created_at"]
        verbose_name = "Task" #Verbose names are how Django shows them in admin.
        verbose_name_plural = "Tasks"
        # Example: avoid duplicate task titles within the same goal
        constraints = [
            models.UniqueConstraint(
                fields=["goal", "title"],
                name="unique_task_title_per_goal",
            ),
            models.CheckConstraint(
                check=~models.Q(title=""),
                name="task_title_not_empty",
            ),
        ]
        indexes = [
            # Helpful composite index for common filters/sorts
            models.Index(fields=["goal", "is_done", "due_date"]),
        ]

    def clean(self):#Any rule you define in the clean() method
        #due date should not be before the goal deadline if both exist
        if self.due_date and self.goal and self.goal.deadline and self.due_date > self.goal.deadline:
            raise ValidationError({"due_date": "Task due date must be on or before the goal deadline."})

    def __str__(self):#String representation for admin/UI.
        return self.title

# This helps with debugging or auditing what’s being created.
@receiver(post_save, sender=Goal)
def log_goal_created(sender, instance: Goal, created: bool, **kwargs):
    if created:
        logger.info(
            "Goal created",
            extra={
                "goal_id": instance.pk,
                "title": instance.title,
                "user_id": instance.user_id,#check this 
                #"goal_id": instance.goal.id,#check this 
                "deadline": instance.deadline.isoformat() if instance.deadline else None,
                "status": instance.status,
            },
        )

