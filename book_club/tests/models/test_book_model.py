"""Unit tests for the book model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from book_club.models import User, Club, Book, UserRating


class UserRatingTestCase(TestCase):
    """Unit tests for the Club model."""

    fixtures = ['book_club/tests/fixtures/default_user.json',
                'book_club/tests/fixtures/second_user.json',
                'book_club/tests/fixtures/books.json']

    def setUp(self):
        self.user = User.objects.get(email="johndoe@example.com")
        self.book = Book.objects.get(ISBN = '0767409752')

# test if its blank
    def test_valid_book(self):
        self._assert_book_is_valid()

    def test_ISBN_must_not_be_blank(self):
        self.book.ISBN = ''
        self._assert_book_is_invalid()

    def test_BookTitle_must_not_be_blank(self):
        self.book.BookTitle = ''
        self._assert_book_is_invalid()

    def test_BookAuthor_must_not_be_blank(self):
        self.book.BookAuthor = ''
        self._assert_book_is_invalid()

    def test_YearOfPublication_must_not_be_blank(self):
        self.book.YearOfPublication = ''
        self._assert_book_is_invalid()

    def test_Publisher_must_not_be_blank(self):
        self.book.Publisher = ''
        self._assert_book_is_invalid()

    def test_ImageURLS_must_not_be_blank(self):
        self.book.ImageURLS = ''
        self._assert_book_is_invalid()

    def test_ImageURLM_must_not_be_blank(self):
        self.book.ImageURLM = ''
        self._assert_book_is_invalid()

    def test_ImageURLL_must_not_be_blank(self):
        self.book.ImageURLL = ''
        self._assert_book_is_invalid()

# test max_length
    def test_ISBN_is_max_length_13(self):
        self.book.ISBN = 'x' * 19
        self._assert_book_is_invalid()

    def test_BookTitle_must_be_max_length_150(self):
        self.book.BookTitle = 'x' * 151
        self._assert_book_is_invalid()

    def test_BookAuthor_must_be_max_length_150(self):
        self.book.BookAuthor = 'x' * 151
        self._assert_book_is_invalid()

    def test_YearOfPublication_must_be_max_length_4(self):
        self.book.YearOfPublication = 'x' * 5
        self._assert_book_is_invalid()

    def test_Publisher_must_be_max_length_150(self):
        self.book.Publisher = 'x' * 151
        self._assert_book_is_invalid()

    def test_ImageURLS_must_be_max_length_300(self):
        self.book.ImageURLS= 'x' * 301
        self._assert_book_is_invalid()

    def test_ImageURLM_must_be_max_length_300(self):
        self.book.ImageURLM = 'x' * 301
        self._assert_book_is_invalid()

    def test_ImageURLL_must_be_max_length_300(self):
        self.book.ImageURLL = 'x' * 301
        self._assert_book_is_invalid()

    def _assert_book_is_valid(self):
        try:
            self.book.full_clean()
        except ValidationError:
            self.fail('Test book should be valid')

    def _assert_book_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.book.full_clean()
