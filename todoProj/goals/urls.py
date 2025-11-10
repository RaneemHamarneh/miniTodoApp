from django.urls import path
from . import views

app_name = 'goals'  # Important for URL namespacing

urlpatterns = [
    # goals
    path("", views.GoalListView.as_view(), name="list"),
    path("new/", views.GoalCreateView.as_view(), name="create_goal"),
    path("<int:pk>/", views.GoalDetailView.as_view(), name="goal_detail"),
    path("<int:pk>/edit/", views.GoalUpdateView.as_view(), name="goal_update"),
   
    # tasks 
    path("tasks/new/<int:goal_id>/", views.TaskCreateView.as_view(), name="task_create"),
    #path("tasks/new/<int:goal_id>/", views.TaskCreateView.as_view(), name="task_create"),
    #path("tasks/new/<int:goal_id>/", views.TaskCreateView.as_view(), name="task_create"),
    
    path("tasks/<int:pk>/edit/", views.TaskUpdateView.as_view(), name="task_update"),
    
    # --- Achievements ---
    path("achievements/", views.AchievementsView.as_view(), name="achievements"),
]
   

