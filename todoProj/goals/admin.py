from django.contrib import admin
from .models import Goal, Task

# Register your models here.
@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'deadline', 'created_at']
    list_filter = ['status']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'goal', 'is_done', 'due_date']
    list_filter = ['is_done', 'goal']
