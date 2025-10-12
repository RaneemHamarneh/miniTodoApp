from django.urls import path
from . import views

app_name = 'goals' 

urlpatterns = [
    path('', views.task_list),
     # If using Function-Based Views:
    path('', views.task_list, name='task_list'), # Example: /goals/
    path('task/<int:task_id>/', views.task_detail, name='task_detail'), # Example: /goals/task/5/

]
