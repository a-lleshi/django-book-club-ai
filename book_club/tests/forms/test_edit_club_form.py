from django import forms
from django.test import TestCase
from book_club.models import User, Club
from book_club.forms import EditClubForm

class EditClubFormTestCase(TestCase):

    fixtures = [
       'book_club/tests/fixtures/default_club.json',
       'book_club/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        self.club = Club.objects.get(name='Horror Club')
        self.form_input = {
           'name': 'Horror Club 2',
           'theme': 'Horror',
           'location': 'London',
           'description': 'Great club!'
        }

    def test_form_has_necessary_fields(self):
        form = EditClubForm()
        self.assertIn('name', form.fields)
        self.assertIn('location', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('theme', form.fields)

    def test_valid_form(self):
        form = EditClubForm(data=self.form_input)
        form.is_valid()
        print(form.errors)
        self.assertTrue(form.is_valid())

    def test_form_uses_model_validation(self):
        self.form_input['name']=''
        form = EditClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        club = Club.objects.get(name='Horror Club')
        form = EditClubForm(instance=club, data=self.form_input)
        before_count = Club.objects.count()
        form.save()
        after_count = Club.objects.count()
        self.assertEqual(before_count, after_count)
        self.assertEqual(club.name, 'Horror Club 2')
        self.assertEqual(club.location, 'London')
        self.assertEqual(club.description, 'Great club!')
        self.assertEqual(club.theme, 'Horror')
