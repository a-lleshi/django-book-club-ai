from django.test import TestCase
from django.urls import reverse
from book_club.models import Club, CurrentlyViewing, User
from book_club.tests.helpers import reverse_with_next
import urllib

class SwitchClubViewTestCase(TestCase):
    """Tests for the switch club view"""

    fixtures = [
        # 'book_club/tests/fixtures/default_user.json',
        'book_club/tests/fixtures/default_club.json',
        'book_club/tests/fixtures/second_user.json',
        'book_club/tests/fixtures/second_club.json',
        # 'book_club/tests/fixtures/other_users.json',
        # 'book_club/tests/fixtures/other_clubs.json',

    ]

    def setUp(self):
        self.club = Club.objects.get(pk=1)
        self.second_club = Club.objects.get(pk=2)
        self.user = User.objects.get(pk=4)
        self.officer = User.objects.get(pk=6)
        self.member = User.objects.get(pk=2)

        CurrentlyViewing.set_currently_viewing(self.user, self.club)
        CurrentlyViewing.set_currently_viewing(self.officer, self.club)
        CurrentlyViewing.set_currently_viewing(self.member, self.club)
        self.url = reverse('switch_club', kwargs={'club_name': self.second_club})

    def test_switch_club_url(self):
        self.assertEqual(urllib.parse.unquote(self.url), f'/switch_club/{self.second_club}')

    def test_get_switch_club_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_switch_club_with_invalid_club_id(self):
        self.client.login(username=self.user.email, password='Password123')
        url = reverse('switch_club', kwargs={'club_name': 'kek'})
        response = self.client.get(url, follow=True)
        response_url = reverse('dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_switch_club_with_user_not_a_member(self):
        self.client.login(username=self.user.email, password='Password123')
        before_club = CurrentlyViewing.get_currently_viewing(self.user)
        url = reverse('switch_club', kwargs={'club_name': self.second_club})
        response = self.client.get(url, follow=True)
        response_url = reverse('dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')
        after_club = CurrentlyViewing.get_currently_viewing(self.user)
        self.assertEqual(before_club, after_club)

    def test_switch_club_switching_to_the_same_club(self):
        self.client.login(username=self.user.email, password='Password123')
        before_club = CurrentlyViewing.get_currently_viewing(self.user)
        url = reverse('switch_club', kwargs={'club_name': self.club})
        response = self.client.get(url, follow=True)
        response_url = reverse('dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')
        after_club = CurrentlyViewing.get_currently_viewing(self.user)
        self.assertEqual(before_club, after_club)

    def test_switch_club_with_valid_id_for_member(self):
        self.client.login(username=self.officer.email, password='Password123')
        before_club = CurrentlyViewing.get_currently_viewing(self.officer)
        url = reverse('switch_club', kwargs={'club_name': self.second_club})
        response = self.client.get(url, follow=True)
        response_url = reverse('dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')
        after_club = CurrentlyViewing.get_currently_viewing(self.officer)
        self.assertNotEqual(before_club, after_club)
