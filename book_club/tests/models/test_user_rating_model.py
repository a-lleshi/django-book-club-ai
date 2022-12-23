"""Unit tests for the user rating model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from book_club.models import User, Club, Book, UserRating


class UserRatingTestCase(TestCase):
    """Unit tests for the Club model."""

    fixtures = ['book_club/tests/fixtures/default_user.json',
                'book_club/tests/fixtures/second_user.json',
                'book_club/tests/fixtures/books.json',
               ]

    def setUp(self):
        self.user = User.objects.get(email="johndoe@example.com")
        self.book = Book.objects.get(ISBN = '0767409752')
        self.rating = UserRating.objects.create(
            userId = self.user.id,
            ISBN = self.book.ISBN,
            bookRating = 3,
        )

    def test_valid_rating(self):
        self._assert_rating_is_valid()

# test if its blank
    def test_userid_must_not_be_blank(self):
        self.rating.userId = ''
        self._assert_rating_is_invalid()

    def test_ISBN_must_not_be_blank(self):
        self.rating.userId = ''
        self._assert_rating_is_invalid()

    def test_bookRating_must_not_be_blank(self):
        self.rating.userId = ''
        self._assert_rating_is_invalid()

# test max_length
    def test_ISBN_must_be_max_length_20(self):
        self.rating.ISBN = 'x' * 21
        self._assert_rating_is_invalid()



    def _assert_rating_is_valid(self):
        try:
            self.rating.full_clean()
        except ValidationError:
            self.fail('Test rating should be valid')

    def _assert_rating_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.rating.full_clean()
