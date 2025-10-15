from django.contrib import admin
from django.urls import path , include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home),
    path('mtable/', views.tasks),
    path('goals', include('goals.urls')),
    path('tasks', include('goals.urls')),
]
