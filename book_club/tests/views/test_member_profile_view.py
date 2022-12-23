"""Unit tests for the Member Profile View."""
from django.conf import settings
from django.test import TestCase
from book_club.models import User, Club
from django.urls import reverse
from book_club.tests.helpers import reverse_with_next

class ClubMemberProfileTestCase(TestCase):
    """Unit tests for the Member Profile View."""

    fixtures = ['book_club/tests/fixtures/default_club.json',
                'book_club/tests/fixtures/second_club.json',
                'book_club/tests/fixtures/default_user.json'
                ]

    def setUp(self):
        self.user = User.objects.get(email="johndoe@example.com")
        self.default_user = User.objects.get(id=1)
        self.default_club = Club.objects.get(id=1)
        self.second_club = Club.objects.get(id=2)
        self.url = reverse('member_info', kwargs={'club_id': self.default_club.id, 'memberid': self.user.id})

    def test_member_profile_url(self):
        correct_url = f'/member_list/member/1/1'
        self.assertEqual(self.url, correct_url)

    def test_get_member_profile_with_valid_id(self):
        self.client.login(email="johndoe@example.com", password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'memberprofile.html')
        self.assertContains(response, "John Doe")

    def test_member_profile_displays_correct_details(self):
        self.client.login(email="johndoe@example.com", password='Password123')
        url = reverse('member_info', kwargs={'club_id': self.default_club.id, 'memberid': self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'memberprofile.html')
        self.assertContains(response, f'{self.default_user.first_name}')
        self.assertContains(response, f'{self.default_user.last_name}')
        self.assertContains(response, f'{self.default_user.age}')
        self.assertContains(response, f'{self.default_club}')

    def test_get_member_profile_with_invalid_id(self):
        self.client.login(email="johndoe@example.com", passsword='Password123')
        url = reverse('member_info', kwargs={'club_id': self.default_club.id, 'memberid': self.user.id+999})
        response = self.client.get(url,follow=True)
        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
