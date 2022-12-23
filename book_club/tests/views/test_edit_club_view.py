"""Tests for the edit club view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from book_club.models import User, Club
from book_club.forms import EditClubForm
from book_club import forms
from book_club.tests.helpers import reverse_with_next

class EditClubViewTestCase(TestCase):

    fixtures = [
      'book_club/tests/fixtures/default_club.json',
      'book_club/tests/fixtures/second_club.json',
      'book_club/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        self.club = Club.objects.get(name='Horror Club')
        self.second_club = Club.objects.get(name='Fantasy Club')
        self.user = User.objects.get(email='johndoe@example.com')
        self.url = reverse('edit_club', kwargs={'club_id': self.club.id})
        self.form_input = {
           'name': 'Horror Club',
           'theme': 'Action',
           'location': 'London',
           'description': 'Great club!'
        }

    def test_get_edit_club_url(self):
        self.assertEqual(self.url, f'/edit_club/{self.club.id}')

    def test_get_edit_club(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditClubForm))

    def test_edit_club_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successful_club_update(self):
        self.client.login(email=self.user.email, password='Password123')
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)

        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)

        self.user.refresh_from_db()
        self.club.refresh_from_db()
        self.assertEqual(self.club.name, 'Horror Club')
        self.assertEqual(self.club.theme, 'Action')
        self.assertEqual(self.club.location, 'London')
        self.assertEqual(self.club.description, 'Great club!')

    def test_unsuccessful_club_update_blank_name(self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['name']=''
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, forms.EditClubForm))
        self.assertTrue(form.is_bound)

        self.club.refresh_from_db()
        self.assertEqual(self.club.name, 'Horror Club')
        self.assertEqual(self.club.theme, 'Horror')
        self.assertEqual(self.club.location, 'Berlin')
        self.assertEqual(self.club.description, 'This book clubs is for those who enjoy to be spooked.')

    def test_unsuccessful_club_update_duplicate_name(self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['name']='Fantasy Club'
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, forms.EditClubForm))
        self.assertTrue(form.is_bound)

        self.club.refresh_from_db()
        self.assertEqual(self.club.name, 'Horror Club')
        self.assertEqual(self.club.theme, 'Horror')
        self.assertEqual(self.club.location, 'Berlin')
        self.assertEqual(self.club.description, 'This book clubs is for those who enjoy to be spooked.')

    def test_unsuccessful_edit_club_when_not_logged_in(self):
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('log_in') + f"?next={self.url}"
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
