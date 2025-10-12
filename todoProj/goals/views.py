from django.shortcuts import render,  get_object_or_404
from django.http import HttpResponse
from .models import Task 

# Create your views here.
# A simple function-based view to display all tasks:cite[2]
def task_list(request):
    """
    View to display a list of all tasks.
    """
    # Get all tasks from the database
    all_tasks = Task.objects.all()
    # Render the 'task_list.html' template, passing the tasks as context
    return render(request, 'goals/goals_list.html', {'task_list': all_tasks})

# A simple function-based view to display the details of a single task:cite[2]
def task_detail(request, task_id):
    """
    View to display the details of a single task.
    The 'task_id' is captured from the URL.
    """
    # Get the task with the specific id, or return a 404 error if not found:cite[2]
    task = get_object_or_404(Task, pk=task_id)
    # Render the 'task_detail.html' template, passing the single task as context
    return render(request, 'goals/task_list.html', {'task': task})