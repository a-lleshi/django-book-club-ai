
"""Unit tests for rating an assigned book."""
from django.conf import settings
from django.test import TestCase
from book_club.models import User, Club, Membership, CurrentlyViewing, Book, UserRating
from django.urls import reverse


class RateAssignedBookTestCase(TestCase):
    """Unit tests for rating assigned books."""

    fixtures = [
        'book_club/tests/fixtures/default_club.json',
        'book_club/tests/fixtures/books.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.owner = User.objects.get(pk=4)
        self.book2 = Book.objects.get(pk=2)
        CurrentlyViewing(user=self.owner, club=self.club).save()
        self.url = reverse('sc_rate_book', kwargs={'book_id': self.book2.id, 'user_rating': "9"})
        self.url2 = reverse('sc_rate_book', kwargs={'book_id': self.book2.id, 'user_rating': "12"})
        self.url3 = reverse('sc_rate_book', kwargs={'book_id': self.book2.id, 'user_rating': "0"})
        self.url4 = reverse('cr_rate_book', kwargs={'book_id': self.book2.id, 'user_rating': "9"})
        self.url5 = reverse('cr_rate_book', kwargs={'book_id': self.book2.id, 'user_rating': "12"})
        self.url6 = reverse('cr_rate_book', kwargs={'book_id': self.book2.id, 'user_rating': "0"})
        self.url7 = reverse('bl_rate_book', kwargs={'book_id': self.book2.id, 'user_rating': "9"})
        self.url8 = reverse('bl_rate_book', kwargs={'book_id': self.book2.id, 'user_rating': "12"})
        self.url9 = reverse('bl_rate_book', kwargs={'book_id': self.book2.id, 'user_rating': "0"})

    def test_rate_assigned_book_url(self):
        correct_url = f'/dashboard/{self.book2.id}/9'
        self.assertEqual(self.url, correct_url)

    def test_check_user_rating_object(self):
        self.client.login(email=self.owner.email, password='Password123')
        response = self.client.get(self.url, follow = True)
        doesRatingExist = UserRating.objects.get(ISBN=self.book2.ISBN, bookRating=9)
        self.assertEqual(doesRatingExist.ISBN,'0192126040')
        self.assertEqual(doesRatingExist.bookRating, 9)
        UserRating.objects.filter(ISBN=self.book2.ISBN, bookRating=9).delete()

    def test_check_user_rating_object_greater_than_10(self):
        self.client.login(email=self.owner.email, password='Password123')
        response = self.client.get(self.url2, follow = True)
        doesRatingExist = UserRating.objects.get(ISBN=self.book2.ISBN, bookRating=10)
        self.assertEqual(doesRatingExist.ISBN,'0192126040')
        self.assertEqual(doesRatingExist.bookRating, 10)
        UserRating.objects.filter(ISBN=self.book2.ISBN, bookRating=10).delete()

    def test_check_user_rating_object_less_than_1(self):
        self.client.login(email=self.owner.email, password='Password123')
        response = self.client.get(self.url3, follow = True)
        doesRatingExist = UserRating.objects.get(ISBN=self.book2.ISBN, bookRating=1)
        self.assertEqual(doesRatingExist.ISBN,'0192126040')
        self.assertEqual(doesRatingExist.bookRating, 1)
        UserRating.objects.filter(ISBN=self.book2.ISBN, bookRating=1).delete()

    def test_check_user_rating_object_in_club_reading_list(self):
        self.client.login(email=self.owner.email, password='Password123')
        response = self.client.get(self.url4, follow = True)
        doesRatingExist = UserRating.objects.get(ISBN=self.book2.ISBN, bookRating=9)
        self.assertEqual(doesRatingExist.ISBN,'0192126040')
        self.assertEqual(doesRatingExist.bookRating, 9)
        UserRating.objects.filter(ISBN=self.book2.ISBN, bookRating=9).delete()

    def test_check_user_rating_object_greater_than_10_in_club_reading_list(self):
        self.client.login(email=self.owner.email, password='Password123')
        response = self.client.get(self.url5, follow = True)
        doesRatingExist = UserRating.objects.get(ISBN=self.book2.ISBN, bookRating=10)
        self.assertEqual(doesRatingExist.ISBN,'0192126040')
        self.assertEqual(doesRatingExist.bookRating, 10)
        UserRating.objects.filter(ISBN=self.book2.ISBN, bookRating=10).delete()

    def test_check_user_rating_object_less_than_1_in_club_reading_list(self):
        self.client.login(email=self.owner.email, password='Password123')
        response = self.client.get(self.url6, follow = True)
        doesRatingExist = UserRating.objects.get(ISBN=self.book2.ISBN, bookRating=1)
        self.assertEqual(doesRatingExist.ISBN,'0192126040')
        self.assertEqual(doesRatingExist.bookRating, 1)
        UserRating.objects.filter(ISBN=self.book2.ISBN, bookRating=1).delete()

    def test_check_user_rating_object_in_book_list(self):
        self.client.login(email=self.owner.email, password='Password123')
        response = self.client.get(self.url7, follow = True)
        doesRatingExist = UserRating.objects.get(ISBN=self.book2.ISBN, bookRating=9)
        self.assertEqual(doesRatingExist.ISBN,'0192126040')
        self.assertEqual(doesRatingExist.bookRating, 9)
        UserRating.objects.filter(ISBN=self.book2.ISBN, bookRating=9).delete()

    def test_check_user_rating_object_greater_than_10_in_book_list(self):
        self.client.login(email=self.owner.email, password='Password123')
        response = self.client.get(self.url8, follow = True)
        doesRatingExist = UserRating.objects.get(ISBN=self.book2.ISBN, bookRating=10)
        self.assertEqual(doesRatingExist.ISBN,'0192126040')
        self.assertEqual(doesRatingExist.bookRating, 10)
        UserRating.objects.filter(ISBN=self.book2.ISBN, bookRating=10).delete()

    def test_check_user_rating_object_less_than_1_in_book_list(self):
        self.client.login(email=self.owner.email, password='Password123')
        response = self.client.get(self.url9, follow = True)
        doesRatingExist = UserRating.objects.get(ISBN=self.book2.ISBN, bookRating=1)
        self.assertEqual(doesRatingExist.ISBN,'0192126040')
        self.assertEqual(doesRatingExist.bookRating, 1)
        UserRating.objects.filter(ISBN=self.book2.ISBN, bookRating=1).delete()
