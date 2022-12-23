"""Unit tests for the Membership model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from book_club.models import User, Club, Membership


class MembershipModelTestCase(TestCase):
    """Unit tests for the Membership model."""

    fixtures = ['book_club/tests/fixtures/default_user.json', 'book_club/tests/fixtures/second_user.json']

    def setUp(self):
        self.user = User.objects.get(email="johndoe@example.com")
        self.second_user = User.objects.get(email="janedoe@example.com")
        self.club = Club.objects.create(
            name='Example book club',
            location='London',
            theme='Python textbooks',
            description='This club is for testing only.'
        )
        self.second_club = Club.objects.create(
            name='A rival book club',
            location='Paris',
            theme='Java textbooks',
            description='This club is also just for testing.'
        )
        self.membership = Membership.objects.create(
            user = self.user,
            club = self.club,
            applicationStatement = 'An example application statement.',
            level = 'APP'
        )
        self.second_membership = Membership.objects.create(
            user = self.second_user,
            club = self.second_club,
            applicationStatement = 'A different example of an application statement.',
            level = 'MEM'
        )

    def test_valid_membership(self):
        self._assert_membership_is_valid()

#User
    def test_user_must_not_be_blank(self):
        self.membership.user = None
        self._assert_membership_is_invalid()

    def test_user_need_not_be_unique(self):
        self.membership.user = self.second_membership.user
        self._assert_membership_is_valid()

# Club
    def test_club_must_not_be_blank(self):
        self.membership.club = None
        self._assert_membership_is_invalid()

    def test_club_need_not_be_unique(self):
        self.membership.club = self.second_membership.club
        self._assert_membership_is_valid()

# Level
    def test_level_must_not_be_blank(self):
        self.membership.level = ''
        self._assert_membership_is_invalid()

    def test_level_need_not_be_unique(self):
        self.membership.level = self.second_membership.level
        self._assert_membership_is_valid()

    def test_level_must_be_a_valid_membership_level(self):
        self.membership.level = 'ABC'
        self._assert_membership_is_invalid()

# Application statement
    def test_applicationStatement_may_be_blank(self):
        self.membership.applicationStatement = ''
        self._assert_membership_is_valid()

    def test_applicationStatement_need_not_be_unique(self):
        self.membership.applicationStatement = self.second_membership.applicationStatement
        self._assert_membership_is_valid()

    def test_applicationStatement_may_contain_1000_characters(self):
        self.membership.applicationStatement = 'x' * 1000
        self._assert_membership_is_valid()

    def test_applicationStatement_may_not_contain_1001_characters(self):
        self.membership.applicationStatement = 'x' * 1001
        self._assert_membership_is_invalid()

# Promotion / Demotion not yet implemented - tests for it should be added here

    def _assert_membership_is_valid(self):
        try:
            self.membership.full_clean()
        except ValidationError:
            self.fail('Test membership should be valid')

    def _assert_membership_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.membership.full_clean()
