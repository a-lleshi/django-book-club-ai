"""Unit tests for the Create Club view."""
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.test import TestCase
from book_club.models import User, Club, Membership
from book_club import forms


class CreateClubViewTestCase(TestCase):
    """Unit tests for the Create Club view."""

    fixtures = ['book_club/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(email="johndoe@example.com")
        self.url = reverse('club.create')
        self.form_input = {
            'name': 'Example name',
            'location': 'Example location',
            'description': 'Example club description.',
            'theme': 'Some theme',
        }

#### GET ###

    def test_create_club_url(self):
        correct_url='/club/create/'
        self.assertEqual(self.url, correct_url)

    def test_get_create_club_view_when_logged_in(self):
        self.client.login(email='johndoe@example.com', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs/create.html')
        form = response.context['form']
    
    def test_get_create_club_view_when_not_logged_in_redirects_to_log_in(self):
        response = self.client.get(self.url)
        response_url = reverse('log_in') + f"?next={self.url}"
        self.assertRedirects(response, response_url,
                             status_code=302, target_status_code=200)

### POST ###

    def test_successful_club_create(self):
        self.client.login(email='johndoe@example.com', password='Password123')
        before_club_count = Club.objects.count()
        before_membership_count = Membership.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_club_count = Club.objects.count()
        after_membership_count = Membership.objects.count()
        # Check that one Club object and one Membership objects were created
        self.assertEqual(after_club_count, before_club_count+1)
        self.assertEqual(after_membership_count, before_membership_count+1)

        # Check that all fields were correctly filled in
        newClub = Club.objects.get(name='Example name')
        self.assertEqual(newClub.location, 'Example location')
        self.assertEqual(newClub.description, 'Example club description.')
        self.assertEqual(newClub.theme, 'Some theme')
        membership = Membership.objects.get(user=self.user, club=newClub)
        self.assertEqual(membership.level, 'OWN')

    def test_unsuccessful_club_create_due_to_duplicate_name(self):
        self.club = Club.objects.create(
            name='Example name', location='A different location', description='A different description', theme='A different theme')
        self.client.login(email='johndoe@example.com', password='Password123')
        before_club_count = Club.objects.count()
        before_membership_count = Membership.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_club_count = Club.objects.count()
        after_membership_count = Membership.objects.count()
        # Check that one Club object and one Membership objects were created
        self.assertEqual(after_club_count, before_club_count)
        self.assertEqual(after_membership_count, before_membership_count)
        # Check that we are redirected to the same page with our incorrect details still filled in
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs/create.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, forms.ClubForm))
        self.assertTrue(form.is_bound)

    def test_unsuccessful_create_club_when_not_logged_in(self):
        before_club_count = Club.objects.count()
        before_membership_count = Membership.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_club_count = Club.objects.count()
        after_membership_count = Membership.objects.count()
        # Check that no Club objects or Membership objects were created
        self.assertEqual(after_club_count, before_club_count)
        self.assertEqual(after_membership_count, before_membership_count)

        response_url = reverse('log_in') + f"?next={self.url}"
        self.assertRedirects(response, response_url,
                             status_code=302, target_status_code=200)