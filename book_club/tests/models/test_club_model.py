"""Unit tests for the Club model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from book_club.models import User, Club


class ClubModelTestCase(TestCase):
    """Unit tests for the Club model."""

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

    def test_valid_club(self):
        self._assert_club_is_valid()

# Name
    def test_name_must_not_be_blank(self):
        self.club.name = ''
        self._assert_club_is_invalid()

    def test_name_must_be_unique(self):
        self.club.name = self.second_club.name
        self._assert_club_is_invalid()

    def test_name_may_contain_100_characters(self):
        self.club.name = 'x' * 100
        self._assert_club_is_valid()

    def test_name_may_not_contain_101_characters(self):
        self.club.name = 'x' * 101
        self._assert_club_is_invalid()

# Location
    def test_location_may_be_blank(self):
        self.club.location = ''
        self._assert_club_is_valid()

    def test_location_need_not_be_unique(self):
        self.club.location = self.second_club.location
        self._assert_club_is_valid()

    def test_location_may_contain_150_characters(self):
        self.club.location = 'x' * 150
        self._assert_club_is_valid()

    def test_location_may_not_contain_151_characters(self):
        self.club.location = 'x' * 151
        self._assert_club_is_invalid()

# Theme
    def test_theme_may_be_blank(self):
        self.club.theme = ''
        self._assert_club_is_valid()

    def test_theme_need_not_be_unique(self):
        self.club.theme = self.second_club.theme
        self._assert_club_is_valid()

    def test_theme_may_contain_100_characters(self):
        self.club.theme = 'x' * 100
        self._assert_club_is_valid()

    def test_theme_may_not_contain_101_characters(self):
        self.club.theme = 'x' * 101
        self._assert_club_is_invalid()

# Description
    def test_description_may_be_blank(self):
        self.club.description = ''
        self._assert_club_is_valid()

    def test_description_need_not_be_unique(self):
        self.club.description = self.second_club.description
        self._assert_club_is_valid()

    def test_description_may_contain_1000_characters(self):
        self.club.description = 'x' * 1000
        self._assert_club_is_valid()

    def test_description_may_not_contain_1001_characters(self):
        self.club.description = 'x' * 1001
        self._assert_club_is_invalid()



    def _assert_club_is_valid(self):
        try:
            self.club.full_clean()
        except ValidationError:
            self.fail('Test club should be valid')

    def _assert_club_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.club.full_clean()
