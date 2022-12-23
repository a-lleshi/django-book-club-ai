"""Dashboard views of the clubs app."""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from book_club.models import CurrentlyViewing,Post,ClubBookAssignment,UserRating,CurrentlyReading
from django.core.exceptions import ObjectDoesNotExist

@login_required
def dashboard(request):
    current_club = CurrentlyViewing.get_currently_viewing(request.user)
    if current_club is None:
        return render(request, 'dashboard.html')

    posts = Post.objects.filter(club=current_club)

    try:
       clubBooks = ClubBookAssignment.objects.filter(clubs=current_club).prefetch_related('ISBN')
    except ObjectDoesNotExist:
       clubBooks = ''

    try:
       userRatedBooks = UserRating.objects.filter(userId=request.user.id).values('ISBN', 'bookRating')
    except ObjectDoesNotExist:
       userRatedBooks = []

    try:
        current_book = CurrentlyReading.get_currently_reading(current_club)
    except ObjectDoesNotExist:
        current_book = None

    return render(request, 'dashboard.html',
                  context={'posts': posts, 'club_books': clubBooks,'userRatedBooks': list(userRatedBooks),
                            'current_book':current_book})
