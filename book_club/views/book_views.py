from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from book_club.models import Book, Club, ClubBookAssignment, UserRating
from django.contrib.auth.mixins import LoginRequiredMixin
from book_club.filters import BookFilter
from book_club.views import FilteredListView
from django.conf import settings
from book_club.tests.helpers import owner_required
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.template.defaulttags import register


@register.filter
def getStarValue(value,args):
    """a view that retuns the type of a star that should be displayed in the book ratings."""
    result = 'unselected'
    avg = float(value)
    compare = float(args)
    difference = avg - compare;

    if( compare <= avg ):
        result = 'selected'
    elif( abs(difference) < 1 and abs(difference) > 0):
        result = 'half'

    return result

@register.filter
def gethalfstar(value,args):
    """A view that returns a boolean depending on whether half a star should be displayed. Used for displaying book ratings."""
    usehalfstar = False;
    difference = float(value) - float(args)
    difference = abs(difference)
    if(difference < 1 and difference > 0):
        usehalfstar = True

    return usehalfstar

class BookListView(LoginRequiredMixin, FilteredListView):
    """A view for showing all books available in the social network"""
    model = Book
    filterset_class = BookFilter
    paginate_by = settings.BOOKS_PER_PAGE
    template_name = 'book_list.html'
    context_object_name = 'books'

    def get_queryset(self, new_qs=None):
        books =  Book.objects.all()
        return super().get_queryset(books)

class BookListViewAssignClass(LoginRequiredMixin, FilteredListView):
    """A view for showing all books available in the social network"""
    model = Book
    filterset_class = BookFilter
    paginate_by = 15
    template_name = 'book_assign.html'
    context_object_name = 'books'
    clubID = None

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        club_id = self.kwargs['club_id']
        context['current_club'] = club_id
        context['booksInThisClub'] = ClubBookAssignment.objects.filter(clubs=club_id).prefetch_related('ISBN')
        return context

    def get_queryset(self, new_qs=None):
        books =  Book.objects.all()
        return super().get_queryset(books)

@login_required
@owner_required
def BookListViewAssign(request, club_id, book_isbn):
    "A view for officers/owners to manually assigning a book for a club to read"
    reqUser = request.user
    qClub = Club.objects.get(id=club_id)

    bookExists = Book.objects.filter(ISBN=book_isbn).exists()

    if (bookExists):
        qBook = Book.objects.get(ISBN=book_isbn)
        ClubBookAssignment.objects.create(clubs=qClub, ISBN=qBook)
        return redirect('book_list_club',club_id)
    else:
        return redirect('book_list_club', club_id)

@login_required
def RateBookSC(request, book_id, user_rating):
    """A view for ratings books depending on the number of stars selected by user. (on dashboard)"""
    reqUser = request.user
    userR = user_rating
    uId= reqUser.id
    qBook = Book.objects.get(id=book_id)
    qISBN= qBook.ISBN
    if (userR > 10):
        userR = 10
    if (userR<1):
        userR = 1
    if (qBook):
        UserRating.objects.create(userId=uId, ISBN=qISBN, bookRating=userR)

    # return redirect('show_club', club_id)
    return redirect('dashboard')

@login_required
def RateBookCR(request, book_id, user_rating):
    """A view for ratings books depending on the number of stars selected by user. (in club reading list)"""
    reqUser = request.user
    userR = user_rating
    uId= reqUser.id
    qBook = Book.objects.get(id=book_id)
    qISBN= qBook.ISBN
    if (userR > 10):
        userR = 10
    if (userR<1):
        userR = 1
    if (qBook):
        UserRating.objects.create(userId=uId, ISBN=qISBN, bookRating=userR)

    return redirect('club_readings')

@login_required
def BookListMoreDetails(request, book_isbn):
    """A view for displaying the details and ratings for a book in a the book list"""
    reqUser = request.user
    uId= reqUser.id

    try:
        qBook = Book.objects.get(ISBN=book_isbn)
    except ObjectDoesNotExist:
        return redirect('book_list')

    # query userrating table for this isbn to get everysingle record of a rating for this isbn
    # then find out how to sum all of these book rating column values for the given results, into an avg,
    # then parse this value to the template to display the avg rating as a number/stars
    records = UserRating.objects.filter(ISBN=book_isbn).values_list('bookRating', flat=True)

    avg = "No ratings"
    if (len(records)>0):
        avg = round((sum(records) / len(records)), 1)
   # get all the books that the logged in user has already rated and add them to the array with the values
    if UserRating.objects.filter(userId=reqUser.id).exists():
        userRatedBooks = UserRating.objects.filter(userId=reqUser.id).values('ISBN', 'bookRating')
    else:
       userRatedBooks = []


    return render(request, 'more_details.html', {'book': qBook, 'userRatedBooks': list(userRatedBooks), 'avg': avg})


@login_required
def RateBookBL(request, book_id, user_rating):
    """A view for ratings books depending on the number of stars selected by user. (in more info page)"""
    reqUser = request.user
    userR = user_rating
    uId= reqUser.id
    qBook = Book.objects.get(id=book_id)
    qISBN= qBook.ISBN

    if (userR > 10):
        userR = 10
    if (userR<1):
        userR = 1
    if (qBook):
        UserRating.objects.create(userId=uId, ISBN=qISBN, bookRating=userR)

    return redirect('more_details', qBook.ISBN)

@login_required
@owner_required
def BookListViewAssignDelete(request, club_id, book_isbn):
    """A view for removing manually assigned books"""
    reqUser = request.user
    qClub = Club.objects.get(id=club_id)
    qBook = Book.objects.get(ISBN=book_isbn)

    if (qBook):
        try:
            ClubBookAssignment.objects.get(clubs=qClub, ISBN=qBook).delete()
        except ObjectDoesNotExist:
            redirect('book_list_club',club_id)

    return redirect('book_list_club', club_id)
