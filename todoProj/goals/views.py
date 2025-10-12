from django.shortcuts import render

# Create your views here.
def goals_list(request):
    return render(request, 'goals/goals_list.html')