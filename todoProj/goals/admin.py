from django.contrib import admin
from .models import Goal, Task

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "status", "deadline", "created_at")
    list_filter = ("status",)
    search_fields = ("title", "user__username")

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "goal", "goal_user", "is_done", "due_date", "created_at")
    list_filter = ("is_done", "goal")
    search_fields = ("title", "goal__title", "goal__user__username")

    def goal_user(self, obj):
        return getattr(obj.goal.user, "username", "-")
    goal_user.short_description = "User"
    goal_user.admin_order_field = "goal__user"