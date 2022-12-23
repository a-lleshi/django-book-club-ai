import random
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from book_club.models import Book, Club, CurrentlyReading, CurrentlyViewing, ClubReadingList, Membership, UserRating

@login_required
def set_reading(request, book_id):
    """ Set the book the club is currently reading """
    try:
        current_club = CurrentlyViewing.get_currently_viewing(request.user)

        if current_club is None:
            messages.warning(request, 'You have currently not selected a club! Select a club to set a book!')
            return redirect('dashboard')

        new_book = Book.objects.get(id=book_id)
        CurrentlyReading.set_currently_reading(current_club, new_book)
        messages.success(request, f'You have set {new_book} as your currently reading book!')

        return redirect('club_readings')
    except ObjectDoesNotExist:
        return redirect('dashboard')

@login_required
def get_club_current_reading(request):
    """ Get the book the club is currently reading """
    current_club = CurrentlyViewing.get_currently_viewing(request.user)
    if current_club is None:
        return render(request, 'club_reading.html')

    try:
       userRatedBooks = UserRating.objects.filter(userId=request.user.id).values('ISBN', 'bookRating')
    except ObjectDoesNotExist:
       userRatedBooks = []

    current_book = CurrentlyReading.get_currently_reading(current_club)
    prev_books_list = ClubReadingList.get_all_books_for_club(current_club)

    if current_book is None:
        if prev_books_list is None:
            return render(request, 'club_reading.html')
        return render(request, 'club_reading.html', {'current_user': request.user, 'prev_books_list': prev_books_list, 'userRatedBooks': list(userRatedBooks)})

    return render(request, 'club_reading.html', {'current_user': request.user, 'prev_books_list': prev_books_list, 'current_book': current_book, 'userRatedBooks': list(userRatedBooks)})

@login_required
def clear_book_add_book(request, book_id):
    """ Clear the currently reading book """
    current_club = CurrentlyViewing.get_currently_viewing(request.user)
    if current_club is None:
        return redirect('club_readings')

    current_book = CurrentlyReading.get_currently_reading(current_club)
    if current_book is None:
        return redirect('club_readings')

    CurrentlyReading.clear_currently_reading(current_book)
    ClubReadingList.save_book_to_reading_list(current_club, current_book)

    # Change user to select reading a book
    club_members = Membership.objects.filter(club=current_club.id,level__in=["MEM","OFF","OWN"]).prefetch_related('user')
    random_user = club_members[random.randint(0, len(club_members) - 1)]
    get_club = Club.objects.get(id=current_club.id)
    get_club.choosing_book_id = random_user.user.id
    get_club.save()
    messages.success(request, f'{random_user.user.full_name()} is now next user to select a book for the club!')

    return redirect('club_readings')
