from django import forms
from .models import Goal, Task

class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ["title", "description", "status", "deadline"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Goal title"}),
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "Describe the goal…"}),
            "deadline": forms.DateInput(attrs={"type": "date"}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "due_date", "is_done"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Task title"}),
            "description": forms.Textarea(attrs={"rows": 3, "placeholder": "Details (optional)"}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }
