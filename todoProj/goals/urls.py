from django.urls import path
from . import views

app_name = 'goals'  # Important for URL namespacing

urlpatterns = [
    # Goal URLs
    path('', views.goal_list, name='list'),  # /goals/
    path('goal/<int:goal_id>/', views.goal_detail, name='goal_detail'),  # /goals/goal/1/
    # Task URLs
    path('tasks/', views.task_list, name='task_list'),  # /goals/tasks/
    path('task/<int:task_id>/', views.task_detail, name='task_detail'),  # /goals/task/1/
]
