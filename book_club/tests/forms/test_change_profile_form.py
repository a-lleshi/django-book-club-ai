"""Unit tests of the user form."""
from django import forms
from django.test import TestCase
from book_club.forms import ProfileForm
from book_club.models import User

class ProfileFormTestCase(TestCase):
    """Unit tests of the user form."""

    fixtures = [
        'book_club/tests/fixtures/default_user.json',
        'book_club/tests/fixtures/second_user.json'
    ]

    def setUp(self):
        self.form_input = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'janedoe@example.com',
            'bio': 'My bio',
            'personal_statement': 'I love books',
            'location': 'London',
            'age': 25
        }
        self.user = User.objects.get(email = 'janedoe@example.com')

    def test_form_has_necessary_fields(self):
        form = ProfileForm()
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('email', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))
        self.assertIn('bio', form.fields)
        bio_widget = form.fields['bio'].widget
        self.assertTrue(isinstance(bio_widget, forms.Textarea))
        self.assertIn('personal_statement', form.fields)
        personal_statement_widget = form.fields['personal_statement'].widget
        self.assertTrue(isinstance(personal_statement_widget, forms.Textarea))
        self.assertIn('location', form.fields)
        self.assertIn('age', form.fields)
        age_field = form.fields['age']
        self.assertTrue(isinstance(age_field, forms.IntegerField))

    def test_valid_user_form(self):
        form = ProfileForm(instance=self.user, data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_uses_model_validation(self):
        self.form_input['email'] = 'janedoeexample.com'
        form = ProfileForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = ProfileForm(instance=self.user, data=self.form_input)
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(self.user.first_name, 'Jane')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.email, 'janedoe@example.com')
        self.assertEqual(self.user.bio, 'My bio')
        self.assertEqual(self.user.personal_statement, 'I love books')
        self.assertEqual(self.user.location, 'London')
        self.assertEqual(self.user.age, 25)
