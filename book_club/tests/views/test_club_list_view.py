"""Unit tests for the Club list."""
from django.conf import settings
from django.test import TestCase
from book_club.models import User, Club
from django.urls import reverse

class ClubListTestCase(TestCase):
    """Unit tests for the Club list."""

    fixtures = ['book_club/tests/fixtures/default_club.json',
                'book_club/tests/fixtures/second_club.json',
                'book_club/tests/fixtures/default_user.json'
                ]

    def setUp(self):
        self.user = User.objects.get(email="johndoe@example.com")
        self.url = reverse('club_list')
        self.default_club = Club.objects.get(id=1)
        self.second_club = Club.objects.get(id=2)
        self.club_list = Club.objects.all()

    def test_club_list_url(self):
        correct_url='/club_list/'
        self.assertEqual(self.url, correct_url)

    def test_get_club_list_view_when_logged_in(self):
        self.client.login(email='johndoe@example.com', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_list.html')

    def test_get_club_list_view_when_not_logged_in_redirects_to_log_in(self):
        response = self.client.get(self.url)
        response_url = reverse('log_in') + f"?next={self.url}"
        self.assertRedirects(response, response_url,
                             status_code=302, target_status_code=200)

    def test_club_list_displays_club_details(self):
        self.client.login(email=self.user.email, password='Password123')
        url = reverse('club_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_list.html')
        self.assertContains(response, f'{self.default_club.name}')
        self.assertContains(response, f'{self.default_club.theme}')
        self.assertContains(response, f'{self.second_club.name}')
        self.assertContains(response, f'{self.second_club.theme}')
