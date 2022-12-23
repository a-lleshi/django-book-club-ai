from django.test import TestCase
from django.urls import reverse
from book_club.models import Post, Club, User, Membership

class NewPostTest(TestCase):

    fixtures = [
        'book_club/tests/fixtures/default_club.json'
        ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(id='2')
        self.club = Club.objects.get(id=1)
        self.url = reverse('new_post', kwargs={'club_id': self.club.id})
        self.data = { 'text': 'The quick brown fox jumps over the lazy dog.' }

    def test_new_post_url(self):
        self.assertEqual(self.url,'/new_post/1')

    # def test_get_new_post_is_forbidden(self):
    #     self.client.login(email=self.user.email, password="Password123")
    #     user_count_before = Post.objects.count()
    #     response = self.client.get(self.url, follow=True)
    #     user_count_after = Post.objects.count()
    #     self.assertEqual(user_count_after, user_count_before)
    #     self.assertEqual(response.status_code, 405)

    def test_post_new_post_redirects_when_not_logged_in(self):
        post_count_before = Post.objects.count()
        redirect_url = '/log_in/?next=/new_post/1'
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url,
            status_code=302, target_status_code=200, fetch_redirect_response=True
        )
        post_count_after = Post.objects.count()
        self.assertEqual(post_count_after, post_count_before)

    def test_successful_new_post(self):
        self.client.login(email=self.user.email, password="Password123")
        post_count_before = Post.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        post_count_after = Post.objects.count()
        self.assertEqual(post_count_after, post_count_before+1)
        new_post = Post.objects.latest('created_at')
        self.assertEqual(self.user, new_post.author)
        response_url = reverse('forum', kwargs={'club_id': self.club.id})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'club_forum.html')

    def test_unsuccessful_new_post(self):
        self.client.login(email='@johndoe', password='Password123')
        post_count_before = Post.objects.count()
        self.data['text'] = ""
        response = self.client.post(self.url, self.data, follow=True)
        post_count_after = Post.objects.count()
        self.assertEqual(post_count_after, post_count_before)
        self.assertTemplateUsed(response, 'log_in.html')

    def test_cannot_create_post_for_other_user(self):
        self.client.login(email=self.user.email, password='Password123')
        other_user = User.objects.get(id=3)
        self.data['author'] = other_user.id
        post_count_before = Post.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        post_count_after = Post.objects.count()
        self.assertEqual(post_count_after, post_count_before+1)
        new_post = Post.objects.latest('created_at')
        self.assertEqual(self.user, new_post.author)
