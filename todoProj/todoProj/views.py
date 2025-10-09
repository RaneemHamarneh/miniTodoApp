# from django.http import HttpResponse
from django.shortcuts import render

def home(request):
    # return HttpResponse("Hello World...\n Our Home Page\n I'm Home ")
    return render(request, 'home.html' )


def tasks(request):
    # return HttpResponse("Tasks ... page")
    return render(request, 'mtable.html')