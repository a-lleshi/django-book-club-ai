from django import forms
from django.forms import ModelForm
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from .models import User, Club, Membership, Event, Post, ClubBookAssignment, UserRating


class BaseModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(BaseModelForm, self).__init__(*args, **kwargs)


class NewPasswordMixin(forms.Form):
    """Form mixing for new_password and password_confirmation fields."""

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
        )]
    )
    password_confirmation = forms.CharField(label='Confirm Password', widget=forms.PasswordInput())

    def clean(self):
        """ Ensure that new_password and password_confirmation contain the same password."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')


class PasswordForm(NewPasswordMixin):
    """Form that allows users to change their password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())
    field_order = ['password', '_all_']

    def __init__(self, user=None, **kwargs):
        """Construct new form instance with a user instance."""

        super().__init__(**kwargs)
        self.user = user

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        password = self.cleaned_data.get('password')
        if self.user is not None:
            user = authenticate(username=self.user.email, password=password)
        else:
            user = None
        if user is None:
            self.add_error('password', "Password is invalid")

    def save(self):
        """Save the user's new password."""

        new_password = self.cleaned_data['new_password']
        if self.user is not None:
            self.user.set_password(new_password)
            self.user.save()
        return self.user


class SignUpForm(NewPasswordMixin, BaseModelForm):
    """Form enabling unregistered users to sign up."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'email', 'bio','age','location','personal_statement']
        widgets = {'bio': forms.Textarea(), 'personal_statement': forms.Textarea()}

    def save(self):
        """Create a new user."""
        super().save(commit=False)
        user = User.objects.create_user(
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            bio=self.cleaned_data.get('bio'),
            age=self.cleaned_data.get('age'),
            location=self.cleaned_data.get('location'),
            password=self.cleaned_data.get('new_password'),
            personal_statement=self.cleaned_data.get('personal_statement'),

        )
        return user

class LogInForm(forms.Form):
    """Form for logging a user into the application."""

    email = forms.EmailField(label='Email', label_suffix='')
    password = forms.CharField(label='Password', label_suffix='', widget=forms.PasswordInput)

    def get_user(self):
        """Return authenticated user if possible."""
        if self.is_valid():
            email = self.cleaned_data.get('email')
            password = self.cleaned_data.get('password')
            return authenticate(email=email, password=password)

class EventForm(ModelForm):
    """Form for creating a new event."""

    class Meta:
        """Form options."""

        model = Event
        fields = ['title', 'description', 'date', 'location']
        labels = {'date': 'YYYY-MM-DD HH:MM:SS'}
        widgets = {'description': forms.Textarea()}

    def save(self):
        """Create a new event."""
        super().save(commit=False)
        event = Event.objects.create(
            title=self.cleaned_data.get('title'),
            description=self.cleaned_data.get('description'),
            date=self.cleaned_data.get('date'),
            location=self.cleaned_data.get('location'),
        )
        return event

class ClubForm(ModelForm):
    """Form for creating a new club."""

    class Meta:
        """Form options."""

        model = Club
        fields = ['name', 'location', 'description', 'theme']
        widgets = {'description': forms.Textarea()}

    def save(self, user):
        """Create a new club."""
        super().save(commit=False)
        new_club = Club.objects.create(
            name=self.cleaned_data.get('name'),
            description=self.cleaned_data.get('description'),
            theme=self.cleaned_data.get('theme'),
            location=self.cleaned_data.get('location'),
            choosing_book_id=user.id,
        )
        Membership.objects.create(
            user=user,
            club=new_club,
            applicationStatement='',
            level='OWN',
        )
        return new_club

class ProfileForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'email', 'bio', 'personal_statement', 'location', 'age']
        widgets = {'bio': forms.Textarea(),
                   'personal_statement': forms.Textarea(),

                  }

class ApplicationForm(forms.ModelForm):
    """Form to apply to be a member of a club."""

    class Meta:
        """Form options."""

        model = Membership
        fields = ['applicationStatement']
        widgets = {'applicationStatement': forms.Textarea()}

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.club = kwargs.pop('club', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        try:
            membership = Membership.objects.get(club=self.club, user=self.user)
            self.add_error('applicationStatement', "You can only complete the application form once!")
        except ObjectDoesNotExist:
            pass

class EditClubForm(forms.ModelForm):
    """Form to update information about clubs."""

    class Meta:
        """Form options."""

        model = Club
        fields = ['name', 'theme', 'location', 'description']
        widgets = { 'description': forms.Textarea() }

class EventForm(ModelForm):
    """Form for creating a new event."""

    class Meta:
        """Form options."""

        model = Event
        fields = ['title', 'description', 'date', 'location', 'clubs']
        labels = {'date': 'YYYY-MM-DD HH:MM:SS'}
        widgets = {'description': forms.Textarea()}

    def save(self):
        """Create a new event."""
        super().save(commit=False)
        event = Event.objects.create(
            title=self.cleaned_data.get('title'),
            description=self.cleaned_data.get('description'),
            date=self.cleaned_data.get('date'),
            location=self.cleaned_data.get('location'),
            clubs=self.cleaned_data.get('clubs'),
        )
        return event

    def __init__(self, club, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        if club == None:
            self.fields['clubs'].queryset = Club.objects.none()
        else:
            self.fields['clubs'].queryset = Club.objects.filter(id=club.id)


class PostForm(forms.ModelForm):
    """Form to ask user for post text.

    The post author must be by the post creator.
    """

    class Meta:
        """Form options."""

        model = Post
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={"rows":3, "cols":20})
        }

class ClubBookAssignment(ModelForm):
    """Form to create a new book assignment for a specific club. """

    class Meta:
        """Form options."""

        model = ClubBookAssignment
        fields = ['clubs', 'ISBN']

    def save(self, user):
        """Create a new book assignment."""
        super().save(commit=False)
        new_book_assignment = ClubBookAssignment.objects.create(
            clubs=self.cleaned_data.get('club'),
            ISBN=self.cleaned_data.get('ISBN'),
        )
        return new_book_assignment

class UserRating(ModelForm):
    """Form to create a new book assignment for a specific club. """

    class Meta:
        """Form options."""

        model = UserRating
        fields = ['userId', 'ISBN', 'bookRating']

    def save(self, user):
        """Create a new book assignment."""
        super().save(commit=False)
        user_rating = UserRating.objects.create(
            userId=self.cleaned_data.get('userId'),
            ISBN=self.cleaned_data.get('ISBN'),
            bookRating=self.cleaned_data.get('userId'),
        )
        return user_rating
