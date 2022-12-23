""""Unit test for the club member demotion"""
from django.test import TestCase
from book_club.models import Club, User, Membership, CurrentlyViewing
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


class ClubMemberDemoteTestCase(TestCase):
    """Unit test for the club member demotion"""

    fixtures = ['book_club/tests/fixtures/default_club.json']

    def setUp(self):
        self.club = Club.objects.get(id = 1)
        self.applicant = Membership.objects.get(user=1, club=1).user
        self.member = Membership.objects.get(user = 2, club = 1).user
        self.officer = Membership.objects.get(user = 3, club = 1).user
        self.owner = Membership.objects.get(user = 4,club = 1).user

        CurrentlyViewing.set_currently_viewing(self.officer, self.club)
        CurrentlyViewing.set_currently_viewing(self.member, self.club)
        CurrentlyViewing.set_currently_viewing(self.applicant, self.club)
        CurrentlyViewing.set_currently_viewing(self.owner, self.club)

        self.url = reverse('club_member_demote', kwargs = {'club_id': self.club.id, 'userid': self.officer.id})

    def test_club_member_demote_url(self):
        correct_url = f'/member_list/1/3'
        self.assertEqual(self.url, correct_url)

    def test_club_demote_redirects_when_not_logged_in(self):
        membership_count_before = Membership.objects.count()
        redirect_url = "/" + settings.LOGIN_URL + f"/?next={self.url}"
        response = self.client.post(self.url, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        membership_count_after = Membership.objects.count()
        self.assertEqual(membership_count_before, membership_count_after)

    def test_officer_is_demoted_to_member_by_owner(self):
        self.client.login(email = self.owner.email, password = 'Password123')
        member = Membership.objects.get(user = 2, club = 1)
        response = self.client.post(self.url, follow = True)
        self.assertEqual(member.level, 'MEM')

    def test_officer_is_demoted_to_member_by_officer(self):
        self.client.login(email = self.officer.email, password = 'Password123')
        member = Membership.objects.get(user = 3, club = 1)
        response = self.client.post(self.url, follow = True)
        self.assertEqual(member.level, 'OFF')
