from django.contrib import messages
from django.test import TestCase
from django.urls import reverse

from book_club.forms import LogInForm
from book_club.models import Club, CurrentlyViewing, User
from book_club.tests.helpers import LogInTester, reverse_with_next


class LogInViewTestCase(TestCase, LogInTester):
    """Test suite for log_in view"""

    fixtures = [
        'book_club/tests/fixtures/default_club.json',
        'book_club/tests/fixtures/second_user.json'
    ]

    def setUp(self):
        self.url = reverse('log_in')
        self.user = User.objects.get(email='Christian.Thompson@example.org')
        self.user_no_clubs = User.objects.get(email='janedoe@example.com')
        self.club = Club.objects.get(pk=1)

    def test_log_in_url(self):
        self.assertEqual(self.url, '/log_in/')

    def test_get_log_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        next = response.context['next']
        self.assertFalse(next)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_get_log_in_with_redirect(self):
        destination_url = reverse('dashboard')
        self.url = reverse_with_next('log_in', destination_url)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        # Also check if form is unbound, no messages.
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        next = response.context['next']
        self.assertEqual(next, destination_url)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_get_log_in_redirects_when_logged_in(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_unsuccessful_log_in(self):
        form_input = {'email': self.user.email, 'password': 'WrongPassword123'}
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_successful_log_in(self):
        form_input = {'email': self.user.email, 'password': 'Password123'}
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_post_log_in_redirects_when_logged_in(self):
        self.client.login(email=self.user.email, password="Password123")
        form_input = {'email': self.user.email, 'password': 'WrongPassword123'}
        response = self.client.post(self.url, form_input, follow=True)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_log_in_with_existing_currently_viewing(self):
        CurrentlyViewing(user=self.user, club=self.club).save()
        form_input = {'email': self.user.email, 'password': 'Password123'}
        cvBeforeLogin = self._assert_currently_viewing_exists()
        self.client.post(self.url, form_input, follow=True)
        cvAfterLogin = self._assert_currently_viewing_exists()
        self.assertEqual(cvBeforeLogin, cvAfterLogin)

    def test_log_in_with_no_currently_viewing(self):
        form_input = {'email': self.user.email, 'password': 'Password123'}
        self._assert_currently_viewing_does_not_exist()
        self.client.post(self.url, form_input, follow=True)
        self._assert_currently_viewing_exists()

    def test_log_in_with_no_currently_viewing_and_no_clubs(self):
        form_input = {'email': self.user_no_clubs.email, 'password': 'Password123'}
        self._assert_currently_viewing_does_not_exist()
        self.client.post(self.url, form_input, follow=True)
        self._assert_currently_viewing_does_not_exist()

    def _assert_currently_viewing_exists(self):
        try:
            cv = CurrentlyViewing.objects.get(user=self.user)
        except CurrentlyViewing.DoesNotExist:
            self.fail('CurrentlyViewing entry does not exist.')
        else:
            return cv

    def _assert_currently_viewing_does_not_exist(self):
        with self.assertRaises(CurrentlyViewing.DoesNotExist):
            CurrentlyViewing.objects.get(user=self.user)
