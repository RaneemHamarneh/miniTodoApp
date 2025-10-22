from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Goal, Task



def goal_list(request):
    """Display all goals with their tasks"""
    goals = Goal.objects.all()
    
    context = {
        'goals': goals,
        'today': timezone.now().date(),
        'total_goals': goals.count(),
        'completed_goals': Goal.objects.filter(status='done').count(),
    }
    return render(request, 'goals/goals_list.html', context)

def goal_detail(request, goal_id):
    """Display single goal with all its tasks"""
    goal = get_object_or_404(Goal, id=goal_id)
    tasks = goal.tasks.all()  # Using related_name="tasks"
    
    context = {
        'goal': goal,
        'tasks': tasks,
        'completed_tasks': tasks.filter(is_done=True).count(),
        'total_tasks': tasks.count(),
        'today': timezone.now().date(),
    }
    return render(request, 'goals/goal_detail.html', context)

def task_list(request):
    """Display all tasks across all goals"""
    tasks = Task.objects.all()
    
    context = {
        'tasks': tasks,
        'completed_tasks': tasks.filter(is_done=True),
        'pending_tasks': tasks.filter(is_done=False),
        'today': timezone.now().date(),
    }
    return render(request, 'goals/task_list.html', context)

def task_detail(request, task_id):
    """Display single task details"""
    task = get_object_or_404(Task, id=task_id)
    
    context = {
        'task': task,
        'today': timezone.now().date(),
    }
    return render(request, 'goals/task_detail.html', context)