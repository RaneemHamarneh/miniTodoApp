from django.contrib import admin
from django.urls import path , include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home),
    # path("accounts/", include("django.contrib.auth.urls")), 
    path('users/', include('users.urls')),
    path('goals/', include('goals.urls')),
]
