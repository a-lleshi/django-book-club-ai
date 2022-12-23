from django.test import TestCase
from django.urls import reverse
from book_club.models import User
from book_club.tests.helpers import LogInTester

class LogOutViewTestCase(TestCase, LogInTester):
    """Test suite for log_out view"""

    fixtures = ['book_club/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('log_out')
        self.user = User.objects.get(email='johndoe@example.com')

    def test_log_out_url(self):
        self.assertEqual(self.url, '/log_out/')

    def test_get_log_out(self):
        self.client.login(username='johndoe@example.com', password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)
        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertFalse(self._is_logged_in())
