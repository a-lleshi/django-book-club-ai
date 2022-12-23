"""Unit tests for the More Details View."""
from django.conf import settings
from django.test import TestCase
from book_club.models import User, Club, Book, UserRating
from django.urls import reverse
from book_club.tests.helpers import reverse_with_next

class MoreDetailsTestCase(TestCase):
    """Unit tests for the More Details View."""

    fixtures = ['book_club/tests/fixtures/default_club.json',
                'book_club/tests/fixtures/books.json',
                'book_club/tests/fixtures/default_user.json',
                'book_club/tests/fixtures/user_rating.json'
                ]

    def setUp(self):
        self.user = User.objects.get(email="johndoe@example.com")
        self.default_user = User.objects.get(id=1)
        self.book1 = Book.objects.get(pk=1)
        self.url = reverse('more_details', kwargs={'book_isbn': self.book1.ISBN})

    def test_more_details_url(self):
        correct_url = f'/book_list/more_details/0767409752'
        self.assertEqual(self.url, correct_url)

    def test_get_more_details_with_valid_isbn(self):
        self.client.login(email="johndoe@example.com", password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'more_details.html')
        self.assertContains(response, "Amazing")

    def test_more_details_displays_correct_details(self):
        self.client.login(email="johndoe@example.com", password='Password123')
        url = reverse('more_details', kwargs={'book_isbn': self.book1.ISBN})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'more_details.html')
        self.assertContains(response, self.book1.ISBN)
        self.assertContains(response, self.book1.BookTitle)
        self.assertContains(response, self.book1.BookAuthor)
        self.assertContains(response, self.book1.YearOfPublication)
        self.assertContains(response, self.book1.ImageURLL)

    def test_more_details_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_book_rated(self):
        self.client.login(email="johndoe@example.com", password='Password123')
        testbookisbn = "0767409752"
        url1 = reverse('more_details', kwargs={'book_isbn': testbookisbn})
        response = self.client.get(url1)
        self.assertContains(response, '<p>You have rated this book as: <b>')

