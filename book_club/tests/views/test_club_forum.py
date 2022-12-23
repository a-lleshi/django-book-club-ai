"""Tests of the feed view."""
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from book_club.forms import PostForm
from book_club.models import User, Club
from book_club.tests.helpers import create_posts, reverse_with_next


class ClubForumViewTestCase(TestCase):
    """Tests of the forum view."""

    fixtures = [
        'book_club/tests/fixtures/default_club.json'
        ]

    def setUp(self):
        self.user = User.objects.get(id=2)
        self.club = Club.objects.get(id=1)
        self.url = reverse('forum', kwargs={'club_id': self.club.id})

    def test_club_forum_url(self):
        self.assertEqual(self.url,'/forum/1')

    def test_get_club_forum(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_forum.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PostForm))
        self.assertFalse(form.is_bound)

    def test_get_club_forum_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
