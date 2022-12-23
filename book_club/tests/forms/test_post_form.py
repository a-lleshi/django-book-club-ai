from django.test import TestCase
from book_club.models import User, Post
from book_club.forms import PostForm

class PostFormTestCase(TestCase):

    fixtures = [
        'book_club/tests/fixtures/default_club.json']

    def setUp(self):
        self.user = User.objects.get(id=2)

    def test_valid_post_form(self):
        input = {'text': 'x'*200 }
        form = PostForm(data=input)
        self.assertTrue(form.is_valid())

    def test_invalid_post_form(self):
        input = {'text': 'x'*600 }
        form = PostForm(data=input)
        self.assertFalse(form.is_valid())
