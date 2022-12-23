from django_filters import CharFilter, ChoiceFilter, FilterSet


from .models import Book,User,Club,Membership


class BookFilter(FilterSet):
    """A filter of book objects by title and author name"""
    BookTitle = CharFilter(label='Title contains: ')
    BookAuthor = CharFilter(label="Author's name contains: ")
    class Meta:
        model = Book
        fields = ['BookTitle','BookAuthor']


class UserFilter(FilterSet):
    """A filter of user objects by name"""

    first_name = CharFilter(field_name='user__first_name')
    last_name = CharFilter(field_name='user__last_name')

    class Meta:
        model = User
        fields = ['first_name','last_name']


class ClubFilter(FilterSet):
    """A filter for club objects by name, location and theme"""

    name = CharFilter(label='Name contains: ')

    class Meta:
        model = Club
        fields = ['name','location','theme']
