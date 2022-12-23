"""Unit tests for the Comment model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from datetime import datetime
from django.utils.timezone import get_current_timezone
from book_club.models import Post, Club, Comment, User, Event, EventComment

class CommentModelTestCase(TestCase):
    """ Comment model test cases """

    fixtures = ['book_club/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(email="johndoe@example.com")
        self.club = Club.objects.create(
            name='Example book club',
            location='London',
            theme='Python textbooks',
            description='This club is for testing only.'
        )
        self.post = Post.objects.create(
            author = self.user,
            club = self.club,
            text = "Example post content"
        )
        self.comment = Comment.objects.create(
            author = self.user,
            text = "Example comment",
            parent_post = self.post
        )

    def test_valid_comment(self):
        self._assert_comment_is_valid()

    def test_text_must_not_be_blank(self):
        self.comment.text = ''
        self._assert_comment_is_invalid()

    def test_text_can_contain_280_characters(self):
        self.comment.text = 'x'*280
        self._assert_comment_is_valid()

    def test_text_cannot_contain_281_characters(self):
        self.comment.text = 'x'*281
        self._assert_comment_is_invalid()

    def test_author_must_not_be_blank(self):
        self.comment.author = None
        self._assert_comment_is_invalid()

    def test_parent_post_must_not_be_blank(self):
        self.comment.parent_post = None
        self._assert_comment_is_invalid()

    def _assert_comment_is_valid(self):
        try:
            self.comment.full_clean()
        except ValidationError:
            self.fail('Test comment should be valid')

    def _assert_comment_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.comment.full_clean()

class EventCommentModelTestCase(TestCase):
    """ EventComment model test cases """

    fixtures = ['book_club/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(email="johndoe@example.com")
        self.club = Club.objects.create(
            name='Example book club',
            location='London',
            theme='Python textbooks',
            description='This club is for testing only.'
        )
        self.event = Event.objects.create(
            title = "Example event",
            description = "Example event content",
            date = datetime.now(tz=get_current_timezone()),
            location = "London",
            clubs = self.club
        )
        self.eventcomment = EventComment.objects.create(
            author = self.user,
            text = "Example eventcomment",
            parent_event = self.event
        )

    def test_valid_eventcomment(self):
        self._assert_eventcomment_is_valid()

    def test_text_must_not_be_blank(self):
        self.eventcomment.text = ''
        self._assert_eventcomment_is_invalid()

    def test_text_can_contain_280_characters(self):
        self.eventcomment.text = 'x'*280
        self._assert_eventcomment_is_valid()

    def test_text_cannot_contain_281_characters(self):
        self.eventcomment.text = 'x'*281
        self._assert_eventcomment_is_invalid()

    def test_author_must_not_be_blank(self):
        self.eventcomment.author = None
        self._assert_eventcomment_is_invalid()

    def test_parent_event_must_not_be_blank(self):
        self.eventcomment.parent_event = None
        self._assert_eventcomment_is_invalid()

    def _assert_eventcomment_is_valid(self):
        try:
            self.eventcomment.full_clean()
        except ValidationError:
            self.fail('Test event eventcomment should be valid')

    def _assert_eventcomment_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.eventcomment.full_clean()