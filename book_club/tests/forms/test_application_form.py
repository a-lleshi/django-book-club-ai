from django import forms
from django.test import TestCase
from book_club.models import User, Club, Membership
from book_club.forms import ApplicationForm
from django.core.exceptions import ObjectDoesNotExist

class ApplicationFormTestCase(TestCase):

    fixtures = [
       'book_club/tests/fixtures/default_club.json',
    ]

    def setUp(self):
        self.club = Club.objects.get(name='Horror Club')
        self.user = User.objects.get(id=5)
        self.form_input = {
           'applicationStatement': 'I would like to join this book club.',
        }

    def test_form_has_necessary_fields(self):
        form = ApplicationForm()
        self.assertIn('applicationStatement', form.fields)

    def test_valid_form(self):
        form = ApplicationForm(data=self.form_input)
        form.is_valid()
        self.assertTrue(form.is_valid())

    def test_form_uses_model_validation(self):
        self.form_input['applicationStatement']=''
        form = ApplicationForm(data=self.form_input)
        self.assertTrue(form.is_valid())
