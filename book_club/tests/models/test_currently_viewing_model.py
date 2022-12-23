"""Unit tests for the Currently Viewing model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from book_club.models import CurrentlyViewing, User, Club


class CurrentlyViewingModelTestCase(TestCase):
    """Unit tests for the Currently Viewing model."""

    fixtures = ['book_club/tests/fixtures/default_user.json',
                'book_club/tests/fixtures/default_club.json',
                'book_club/tests/fixtures/second_user.json',
                'book_club/tests/fixtures/second_club.json']

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.club = Club.objects.get(pk=1)
        self.second_club = Club.objects.get(pk=2)
        self.session = CurrentlyViewing.set_currently_viewing(self.user, self.club)

    def test_session_is_valid(self):
        self._assert_session_is_valid()

    def test_session_user_must_not_be_blank(self):
        with self.assertRaises(ValueError):
            self.session.user = ""

    def test_session_user_must_not_be_none(self):
        self.session.user = None
        self._assert_session_is_invalid()

    def test_sessions_cannot_have_same_user(self):
        s = CurrentlyViewing(self.user, self.second_club)
        s.save()
        self.assertEqual(len(CurrentlyViewing.objects.filter(user=self.user)),1)

    def test_sessions_cannot_have_blank_club(self):
        with self.assertRaises(ValueError):
            self.session.club = ""

    def test_sessions_can_have_none_club(self):
        self.session.club = None
        self._assert_session_is_valid()

    def test_can_change_club_in_session(self):
        self.session = CurrentlyViewing.set_currently_viewing(self.user, self.second_club)
        self._assert_session_is_valid()

    def _assert_session_is_valid(self):
        try:
            self.session.full_clean()
        except ValidationError:
            self.fail('Test session should be valid')

    def _assert_session_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.session.full_clean()
