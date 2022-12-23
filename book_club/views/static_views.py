"""Static views of the book club app."""
from django.shortcuts import render

from book_club.helpers import login_prohibited
from book_club.models import *

@login_prohibited
def home(request):
    return render(request, 'home.html')
