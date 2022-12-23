from django.test import TestCase
from django.urls import reverse
from datetime import datetime
from django.utils.timezone import get_current_timezone
from book_club.models import Event, Club, User, Membership, EventComment
from book_club import forms

class NewEventCommentTest(TestCase):

    fixtures = [
        'book_club/tests/fixtures/default_club.json'
        ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(id='2')
        self.club = Club.objects.get(id=1)
        self.event = Event.objects.create(
            title = "Example event",
            description = "Example event content",
            date = datetime.now(tz=get_current_timezone()),
            location = "London",
            clubs = self.club
        )
        self.url = reverse('new_event_comment', kwargs={'event_id': self.event.id})
        self.data = { 'text': 'The quick brown fox jumps over the lazy dog.' }

    def test_new_comment_url(self):
        self.assertEqual(self.url,'/new_event_comment/1')

    # def test_get_new_post_is_forbidden(self):
    #     self.client.login(email=self.user.email, password="Password123")
    #     user_count_before = Post.objects.count()
    #     response = self.client.get(self.url, follow=True)
    #     user_count_after = Post.objects.count()
    #     self.assertEqual(user_count_after, user_count_before)
    #     self.assertEqual(response.status_code, 405)

    def test_get_new_event_comment(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event_list.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, forms.PostForm))

    def test_post_new_event_comment_redirects_when_not_logged_in(self):
        comment_count_before = EventComment.objects.count()
        redirect_url = '/log_in/?next=/new_event_comment/1'
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url,
            status_code=302, target_status_code=200, fetch_redirect_response=True
        )
        comment_count_after = EventComment.objects.count()
        self.assertEqual(comment_count_after, comment_count_before)

    def test_successful_new_event_comment(self):
        self.client.login(email=self.user.email, password="Password123")
        comment_count_before = EventComment.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        comment_count_after = EventComment.objects.count()
        self.assertEqual(comment_count_after, comment_count_before+1)
        new_comment = EventComment.objects.latest('created_at')
        self.assertEqual(self.user, new_comment.author)
        self.assertEqual(self.event, new_comment.parent_event)
        self.assertEqual('The quick brown fox jumps over the lazy dog.', new_comment.text)
        self.assertNotEqual(None, new_comment.created_at)
        response_url = reverse('event_list')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'event_list.html')

    def test_unsuccessful_new_event_comment(self):
        self.client.login(email='@johndoe', password='Password123')
        comment_count_before = EventComment.objects.count()
        self.data['text'] = ""
        response = self.client.post(self.url, self.data, follow=True)
        comment_count_after = EventComment.objects.count()
        self.assertEqual(comment_count_after, comment_count_before)
        self.assertTemplateUsed(response, 'log_in.html')

    def test_cannot_create_event_comment_for_other_user(self):
        self.client.login(email=self.user.email, password='Password123')
        other_user = User.objects.get(id=3)
        self.data['author'] = other_user.id
        comment_count_before = EventComment.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        comment_count_after = EventComment.objects.count()
        self.assertEqual(comment_count_after, comment_count_before+1)
        new_comment = EventComment.objects.latest('created_at')
        self.assertEqual(self.user, new_comment.author)
