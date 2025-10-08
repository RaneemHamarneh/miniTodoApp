from django.http import HttpResponse

def home(Request):
    return HttpResponse("Hello World...\n Our Home Page\n I'm Home ")


def tasks(Request):
    return HttpResponse("Tasks ... page")