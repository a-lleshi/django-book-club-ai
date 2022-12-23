"""Tests for the profile view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from book_club.forms import ProfileForm
from book_club.models import User
from book_club.tests.helpers import reverse_with_next

class ProfileViewTestCase(TestCase):
    """Test suite for the profile view."""

    fixtures = [
        'book_club/tests/fixtures/default_user.json',
        'book_club/tests/fixtures/second_user.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.com')
        self.url = reverse('change_profile')
        self.form_input = {
            'first_name': 'Janer',
            'last_name': 'Doer',
            'email': 'janedoe2@example.org',
            'bio': 'My bio new',
            'personal_statement': 'I love books innit',
            "age": 24 ,
            "location": "Cachaca",

        }

    def test_profile_url(self):
        self.assertEqual(self.url, '/profile/change_profile/')

    def test_get_profile(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/change_profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ProfileForm))
        self.assertEqual(form.instance, self.user)

    def test_get_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_unsuccesful_profile_update(self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['email'] = 'johndoexample.com'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/change_profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ProfileForm))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.email, 'johndoe@example.com')
        self.assertEqual(self.user.bio, "Hey, I'm John Doe.")
        self.assertEqual(self.user.personal_statement ,"Boooooooooooks")
        self.assertEqual(self.user.age, 23)
        self.assertEqual(self.user.location, "Berlin")


    def test_unsuccessful_profile_update_due_to_duplicate_email(self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['email'] = 'janedoe@example.com'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/change_profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ProfileForm))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.email, 'johndoe@example.com')
        self.assertEqual(self.user.bio, "Hey, I'm John Doe.")
        self.assertEqual(self.user.personal_statement ,"Boooooooooooks")
        self.assertEqual(self.user.age, 23)
        self.assertEqual(self.user.location, "Berlin")

    def test_succesful_profile_update(self):
        self.client.login(email=self.user.email, password='Password123')
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.user.refresh_from_db()

        self.assertEqual(self.user.first_name, 'Janer')
        self.assertEqual(self.user.last_name, 'Doer')
        self.assertEqual(self.user.email, 'janedoe2@example.org')
        self.assertEqual(self.user.bio, "My bio new")
        self.assertEqual(self.user.personal_statement ,"I love books innit")
        self.assertEqual(self.user.age, 24)
        self.assertEqual(self.user.location, "Cachaca")

    def test_post_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
