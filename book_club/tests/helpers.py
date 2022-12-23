from django.conf import settings
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from book_club.models import  User, Membership, Club, Book
import urllib


def reverse_with_next(url_name, next_url):
    return reverse(url_name) + f"?next={urllib.parse.quote_plus(next_url)}"


class LogInRequiredTests(object):
    """
    Class for automatically testing `@login_required` views.

    Subclasses must implement:
        * `self.user`
        * `self.url` (e.g. `reverse('dashboard')`)
        * `self.url_string` (e.g. `'/dashboard/'`)
        * `self.template_name` (e.g. `'dashboard.html'`)
    """

    def test_view_url(self):
        self._assert_fully_implemented()
        self.assertEqual(self.url, self.url_string)

    def test_get_view(self):
        self._assert_fully_implemented()
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)

    def test_get_view_redirects_when_not_logged_in(self):
        self._assert_fully_implemented()
        redirect_url = reverse_with_next(settings.LOGIN_URL, self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def _assert_fully_implemented(self):
        if not all(hasattr(self, attr) for attr in ['url', 'user', 'url_string', 'template_name']):
            raise NotImplementedError(f'self.url, self.user, self.url_string and self.template_name must be in setUp()')

class LogInTester:
    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()


"""User needs to be an owner or an officer to access."""
def owner_required(view_function, *args, **kwargs):
    def modified_view_function(request, *args, **kwargs):
        user = request.user
        club_id = kwargs['club_id']
        current_club = None
        try:
            current_club = Club.objects.get(id=club_id)
        except ObjectDoesNotExist:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)

        try:
            membership = Membership.objects.get(club=current_club, user=user)
        except ObjectDoesNotExist:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)

        if not (membership.level == 'OWN' or membership.level == 'OFF'):
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request, *args, **kwargs)
    return modified_view_function


"""User is required not to have a membership already for a particular club."""
def no_membership_required(view_function, *args, **kwargs):
    def modified_view_function(request, *args, **kwargs):
        user = request.user
        club_id = kwargs['club_id']
        current_club = None
        try:
            current_club = Club.objects.get(id=club_id)
        except ObjectDoesNotExist:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)

        try:
            membership = Membership.objects.get(club=current_club, user=user)
            return redirect('club_list')

        except ObjectDoesNotExist:
            return view_function(request, *args, **kwargs)
    return modified_view_function


def _create_test_books(self, owner, book_count = 10):
    books = []
    for book_id in range(book_count):
        c = Book(
            ISBN = f"{book_id}",
            BookTitle = f'Book {book_id}',
            BookAuthor = f'Author {book_id}',
            YearOfPublication = '2002',
            Publisher = f"Publisher {book_id}",
            ImageURLS = "url",
            ImageURLM = "url",
            ImageURLL = "url"

        )
        c.save()
        books.append(c)
    return books


def create_posts(author, from_count, to_count):
    """Create unique numbered posts for testing purposes."""
    for count in range(from_count, to_count):
        text = f'Post__{count}'
        post = Post(author=author, text=text)
        post.save()
