from django.test import TestCase
from django.urls import reverse
from book_club.models import User, Club, Membership, CurrentlyViewing
from book_club.tests.helpers import reverse_with_next
from django.conf import settings

class ClubMemberListTestCase(TestCase):
    """Unit tests for the Member list."""

    fixtures = ['book_club/tests/fixtures/default_club.json']

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.applicant = Membership.objects.get(user=1, club=1).user
        self.member = Membership.objects.get(user=2, club=1).user
        self.officer = Membership.objects.get(user=3, club=1).user
        self.owner = Membership.objects.get(user=4,club=1).user
        CurrentlyViewing(user=self.officer, club=self.club).save()
        CurrentlyViewing(user=self.owner, club=self.club).save()
        CurrentlyViewing(user=self.member, club=self.club).save()
        CurrentlyViewing(user=self.applicant, club=self.club).save()

        self.url = reverse('club_member_list')

    def test_applicant_list_url(self):
        correct_url = '/member_list/'
        self.assertEqual(self.url, correct_url)

    def test_get_club_memberlist_list_as_owner(self):
        self.client.login(email=self.owner.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_member_list.html')

    def test_get_club_memberlist_as_officer(self):
        self.client.login(email=self.officer.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_member_list.html')

    def test_get_club_memberlist_as_member(self):
        self.client.login(email=self.member.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_member_list.html')

    def test_get_club_memberlist_as_applicant(self):
        self.client.login(email=self.applicant.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_member_list.html')

    def test_get_member_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302,target_status_code=200)

    # def test_get_club_memberlist_view_when_not_a_member_of_club(self):
    #     self.client.login(email='johndoe@example.com', password='Password123')
    #     response = self.client.get(self.url)
    #     response_url = reverse('club_list') + f"?next={self.url}"
    #     self.assertRedirects(response, response_url,
    #                          status_code=302, target_status_code=200)

    def test_get_club_memberlist_view_when_not_logged_in_redirects_to_log_in(self):
        response = self.client.get(self.url)
        response_url = reverse('log_in') + f"?next={self.url}"
        self.assertRedirects(response, response_url,
                             status_code=302, target_status_code=200)
