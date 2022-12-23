from django.test import TestCase
from django.urls import reverse
from book_club.models import User

class HomeViewTestCase(TestCase):
    """Test suite for home view"""

    fixtures = ['book_club/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.com')
        self.url = reverse('home')

    def test_home_url(self):
        self.assertEqual(self.url, '/')

    def test_get_home(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_get_home_redirects_when_logged_in(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')
