"""Unit tests for the Event model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from datetime import datetime
from django.utils.timezone import get_current_timezone
from book_club.models import Club, Event

class EventModelTestCase(TestCase):
    """ Event model test cases """

    fixtures = ['book_club/tests/fixtures/default_club.json']

    def setUp(self):
        self.club = Club.objects.get(pk=1)
        self.event = Event.objects.create(title="Test Event", description="Test Description", date=datetime.now(tz=get_current_timezone()), location="Online", clubs=self.club)

    def test_valid_event(self):
        self._assert_event_is_valid()

    def test_title_must_not_be_blank(self):
        self.event.title = ''
        self._assert_event_is_invalid()

    def test_title_must_contain_100_characters(self):
        self.event.title = 'x' * 99
        self._assert_event_is_valid()

    def test_title_must_not_contain_more_than_100_characters(self):
        self.event.title = 'x' * 101
        self._assert_event_is_invalid()

    def test_description_must_not_be_blank(self):
        self.event.description = ''
        self._assert_event_is_invalid()

    def test_description_must_contain_520_characters(self):
        self.event.description = 'x' * 519
        self._assert_event_is_valid()

    def test_description_must_not_contain_more_than_520_characters(self):
        self.event.description = 'x' * 521
        self._assert_event_is_invalid()

    def test_date_must_not_be_blank(self):
        self.event.date = ''
        self._assert_event_is_invalid()

    def test_date_must_be_valid(self):
        self.event.date = '2019-01-01'
        self._assert_event_is_valid()

    def test_date_must_not_be_invalid(self):
        self.event.date = 'not a date'
        self._assert_event_is_invalid()

    def test_location_must_not_be_blank(self):
        self.event.location = ''
        self._assert_event_is_invalid()

    def test_location_must_contain_30_characters(self):
        self.event.location = 'x' * 29
        self._assert_event_is_valid()

    def test_location_must_not_contain_more_than_30_characters(self):
        self.event.location = 'x' * 31
        self._assert_event_is_invalid()

    def _assert_event_is_valid(self):
        try:
            self.event.full_clean()
        except ValidationError:
            self.fail('Test event should be valid')

    def _assert_event_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.event.full_clean()
