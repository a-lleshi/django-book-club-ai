"""Unit tests of the event form."""
from django import forms
from django.test import TestCase
from book_club.forms import EventForm
from book_club.models import Event,Club
import datetime

class AddEventFormTestCase(TestCase):
    """Unit tests of the user form."""

    fixtures = [
        'book_club/tests/fixtures/default_club.json',
    ]

    def setUp(self):
        self.form_input = {
            'title': 'New event name',
            'description': 'New event description',
            'date':"2022-09-09",
            'location':"Office",
            'clubs': 1
        }

    def test_form_has_necessary_fields(self):
        form = EventForm(club=Club.objects.get(pk=1))
        self.assertIn('title', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('date', form.fields)
        self.assertIn('location', form.fields)

    def test_valid_event_form(self):
        form = EventForm(club=Club.objects.get(pk=1),data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_uses_model_validation(self):
        self.form_input['date'] = None
        form = EventForm(club=Club.objects.get(pk=1),data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = EventForm(club=Club.objects.get(pk=1), data=self.form_input)
        before_count = Event.objects.count()
        form.save()
        after_count = Event.objects.count()
        self.assertEqual(after_count-1, before_count)
        event = list(Event.objects.all())[0]
        self.assertEqual(event.title, 'New event name')
        self.assertEqual(event.description, 'New event description')
        self.assertEqual(event.location,'Office')
