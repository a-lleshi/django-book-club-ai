"""Unit tests for rating a book."""
from django.conf import settings
from django.test import TestCase
from book_club.models import User, Club, Membership, CurrentlyViewing, Book, UserRating
from django.urls import reverse
from book_club.views.book_views import gethalfstar,getStarValue


class RateBookTestCase(TestCase):
    """Unit tests for rating books."""

    fixtures = [
        'book_club/tests/fixtures/default_club.json',
        'book_club/tests/fixtures/books.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.owner = User.objects.get(pk=4)
        self.book1 = Book.objects.get(pk=1)
        CurrentlyViewing(user=self.owner, club=self.club).save()
        self.url = reverse('bl_rate_book', kwargs={'book_id': self.book1.id, 'user_rating': "6"})

    def test_rate_book_url(self):
        correct_url = f'/book_list/more_details/1/6'
        self.assertEqual(self.url, correct_url)

    def test_check_rating_object(self):
        self.client.login(email=self.owner.email, password='Password123')
        response = self.client.post(self.url, follow = True)
        doesRatingExist = UserRating.objects.get(ISBN=self.book1.ISBN, bookRating=6)
        self.assertEqual(doesRatingExist.ISBN,'0767409752')
        self.assertEqual(doesRatingExist.bookRating, 6)

    def test_halfstar_value_returns_correct_result(self):
        self.client.login(email=self.owner.email, password='Password123')
        self.assertEqual(False,gethalfstar(3,3))

    def test_halfstar_value_returns_correct_result(self):
        self.client.login(email=self.owner.email, password='Password123')
        self.assertEqual(True,gethalfstar(3,2.5))

    def test_getStarValue_returns_correct_result(self):
        self.client.login(email=self.owner.email, password='Password123')
        self.assertEqual('selected',getStarValue(3,3))

    def test_getStarValue_returns_correct_result(self):
        self.client.login(email=self.owner.email, password='Password123')
        self.assertEqual('half',getStarValue(6,6.5))
