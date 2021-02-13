from django.shortcuts import render
from django.http import HttpResponse

posts = [
    {
        "author": "Me",
        "post": "Lroem ipsum"
    },
    {
        "author": "You",
        "post": "Lroem ipsum Amet"
    }


]

def home(request):
    context = {
        'posts': posts
    }
    return render(request, "home/home.html", context)
