"""Tests for the show club view."""
from django.test import TestCase
from django.urls import reverse
from book_club.models import User, Club
from book_club.tests.helpers import reverse_with_next

class ShowClubViewTestCase(TestCase):

    fixtures = [
      'book_club/tests/fixtures/default_club.json',
      'book_club/tests/fixtures/default_user.json',

    ]

    def setUp(self):
        self.club = Club.objects.get(name='Horror Club')
        self.user = User.objects.get(email='johndoe@example.com')
        self.url = reverse('show_club', kwargs={'club_id': self.club.id})

    def test_get_show_club_url(self):
        self.assertEqual(self.url, f'/show_club/{self.club.id}')

    def test_get_show_club(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_club.html')

    def test_show_club_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_show_club_displays_club_details(self):
        self.client.login(email=self.user.email, password='Password123')
        url = reverse('show_club', kwargs={'club_id': self.club.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_club.html')
        self.assertContains(response, f'{self.club.name}')
        self.assertContains(response, f'{self.club.theme}')
        self.assertContains(response, f'{self.club.location}')
        self.assertContains(response, f'{self.club.description}')
