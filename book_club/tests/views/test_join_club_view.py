"""Unit test for the Join club view"""
from django.test import TestCase
from book_club.models import Club, User, Membership
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


class JoinClubViewTestCase(TestCase):
    """Unit test for the Join club view"""

    fixtures = [
        'book_club/tests/fixtures/default_club.json']

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.form_input = {
            'applicationStatement': 'I would like to join this club.',
        }
        self.applicant = User.objects.get(id=1)
        self.not_an_applicant = User.objects.get(id=5)
        self.url = reverse('join', kwargs={'club_id': self.club.id})



    def test_club_list_url(self):
        correct_url='/join/1'
        self.assertEqual(self.url, correct_url)

    def test_get_join_club(self):
        self.client.login(email=self.not_an_applicant.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'apply.html')

    def test_join_club_redirects_when_not_logged_in(self):
        membership_count_before = Membership.objects.count()
        redirect_url = "/" + settings.LOGIN_URL + f"/?next={self.url}"
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        membership_count_after = Membership.objects.count()
        self.assertEqual(membership_count_before, membership_count_after)

    def test_post_join_club_redirects_when_applicant(self):
        self.client.login(email=self.applicant.email, password='Password123')
        membership_count_before = Membership.objects.count()
        redirect_url = reverse('club_list')
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        membership_count_after = Membership.objects.count()
        self.assertEqual(membership_count_before, membership_count_after)


    def test_post_successful_join_club(self):
        self.client.login(email=self.not_an_applicant.email, password='Password123')
        redirect_url = reverse('club_list')
        form_input = {'applicationStatement': 'I would like to join this club.', 'next': redirect_url}
        membership_count_before = Membership.objects.count()
        response = self.client.post(self.url, form_input, follow = True)
        membership_count_after = Membership.objects.count()
        self.assertEqual(membership_count_after, membership_count_before+1)

        self.assertRedirects(
            response, redirect_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        membership = None
        try:
            membership = Membership.objects.get(user=self.not_an_applicant, club=self.club)
        except ObjectDoesNotExist:
            self.fail("User is not an applicant!")

        self.assertEqual(membership.level, 'APP')
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club_list.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)
        """User should not be able to complete the form twice."""
        response = self.client.post(self.url, form_input, follow = True)
        self.assertRedirects(
            response, redirect_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
