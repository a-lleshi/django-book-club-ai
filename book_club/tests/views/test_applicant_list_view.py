"""Unit tests for the Applicant list."""
from django.conf import settings
from django.test import TestCase
from book_club.models import User, Club, Membership, CurrentlyViewing
from django.urls import reverse

class ApplicantListTestCase(TestCase):
    """Unit tests for the Applicant list."""

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

        self.url = reverse('applicant_list')

    def test_get_applicant_list_as_owner(self):
        self.client.login(email=self.owner.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applicant_list.html')

    def test_get_applicant_list_as_officer(self):
        self.client.login(email=self.officer.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applicant_list.html')

    def test_member_can_not_access_applicant_list(self):
        self.client.login(email=self.member.email, password="Password123")
        response = self.client.get(self.url)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200)

    def test_applicant_can_not_access_applicant_list(self):
        self.client.login(email=self.applicant.email, password="Password123")
        response = self.client.get(self.url)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200)

    def test_applicant_list_url(self):
        self.assertEqual(self.url, '/applicant_list/')
