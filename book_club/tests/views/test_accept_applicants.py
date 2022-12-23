"""Unit tests for the accepting applicants."""
from django.conf import settings
from django.test import TestCase
from book_club.models import User, Club, Membership,CurrentlyViewing
from django.urls import reverse

from book_club.views.club_application_views import accept_applicant

class AcceptApplicantsTestCase(TestCase):
    """Unit tests for the accepting applicants."""

    fixtures = ['book_club/tests/fixtures/default_club.json']

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.applicant = User.objects.get(pk=1) #Membership.objects.get(user=1, club=1).user
        self.member = User.objects.get(pk=2) #Membership.objects.get(user=2, club=1).user
        self.officer = User.objects.get(pk=3) #Membership.objects.get(user=3, club=1).user
        self.owner = User.objects.get(pk=4) #Membership.objects.get(user=4,club=1).user
        CurrentlyViewing(user=self.officer, club=self.club).save()
        CurrentlyViewing(user=self.owner, club=self.club).save()
        CurrentlyViewing(user=self.member, club=self.club).save()
        self.url = reverse(accept_applicant, kwargs={'club_id': self.club.id, 'user_id': self.applicant.id})

    def test_accept_applicants_url(self):
        correct_url = f'/accept_applicant/club=1&user=1'
        self.assertEqual(self.url, correct_url)

    def test_applicant_is_promoted_to_member_by_owner(self):
        self.client.login(email=self.owner.email, password='Password123')
        applicantBefore = Membership.objects.get(user=1, club=1)
        response = self.client.post(self.url, follow = True)
        applicantAfter = Membership.objects.get(user=1, club=1)
        self.assertEqual(applicantBefore.level,'APP')
        self.assertEqual(applicantAfter.level, 'MEM')

    def test_applicant_is_promoted_to_member_by_officer(self):
        self.client.login(email=self.officer.email, password='Password123')
        applicantBefore = Membership.objects.get(user=1, club=1)
        response = self.client.post(self.url, follow = True)
        applicantAfter = Membership.objects.get(user=1, club=1)
        self.assertEqual(applicantBefore.level,'APP')
        self.assertEqual(applicantAfter.level, 'MEM')

    def test_applicant_is_promoted_to_member_by_member(self):
        self.client.login(email=self.member.email, password='Password123')
        applicantBefore = Membership.objects.get(user=1, club=1)
        response = self.client.post(self.url, follow = True)
        applicantAfter = Membership.objects.get(user=1, club=1)
        self.assertEqual(applicantBefore.level,'APP')
        self.assertEqual(applicantAfter.level, 'APP')
