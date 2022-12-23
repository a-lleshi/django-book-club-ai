from pydoc import describe
from re import U
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator
from django.db import models
from libgravatar import Gravatar


class UserManager(BaseUserManager):  # pragma: no cover
    """Manager for the User model"""

    def create_user(self, email, first_name, last_name, personal_statement,
                    bio="",age = None, location = "", password=None, is_staff=False,
                    is_superuser=False):
        """
        Creates and saves a User with the given email and other fields.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            personal_statement=personal_statement,
            bio=bio,
            age=age,
            location=location,
            is_active=True,
            is_staff=is_staff,
            is_superuser=is_superuser
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None):
        """
        Creates and saves a superuser with the given email, first_name, last_name and password.
        """
        user = self.create_user(
            email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            personal_statement="I am an admin",
            age=999,
            bio="",
            is_staff=True,
            is_superuser=True,
        )
        user.save(using=self._db)
        return user


class User(AbstractUser):
    """User model used for authentication"""

    class Meta:
        ordering = ['last_name', 'first_name']

    username = None
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)
    bio = models.CharField(max_length=520, blank=True)
    personal_statement = models.CharField(max_length=520, blank=False, help_text='This statement is sent to any clubs you apply to. It can be changed at any time.')
    location = models.CharField(max_length=30, blank=False)
    age = models.IntegerField(blank=True)

    USERNAME_FIELD = 'email'

    # For createsuperuser command. Email and password fields asked for by default.
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        return self.gravatar(size=60)

    def large_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        return self.gravatar(size=200)

    def micro_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        return self.gravatar(size=25)


class Club(models.Model):
    """Club model"""

    name = models.CharField(max_length=100, unique=True, blank=False)
    location = models.CharField(max_length=150, blank=True, unique=False)
    description = models.CharField(max_length=1000, blank=True, unique=False)
    theme = models.CharField(max_length=100, blank=True, unique=False)
    choosing_book = models.ForeignKey(User, on_delete=models.CASCADE,default=1)


    class Meta:
        ordering = ['name','location','theme']

    def owner(self):
        if not hasattr(self, 'ownerData'):
            self.ownerData = self.membership_set.filter(
                level=Membership.MembershipLevels.OWNER).first()
        return self.ownerData

    def getAdministrators(self):
        return self.membership_set.filter(models.Q(level=Membership.MembershipLevels.OFFICER) | models.Q(level=Membership.MembershipLevels.OWNER))

    def getMembers(self):
        return self.membership_set.filter(models.Q(level=Membership.MembershipLevels.MEMBER))

    def getApplicants(self):
        return self.membership_set.filter(models.Q(level=Membership.MembershipLevels.APPLICANT))

    def getId(self):
        return self.id

    def __str__(self):
        return self.name

class Membership(models.Model):

    class MembershipLevels(models.TextChoices):
        APPLICANT = 'APP', 'Applicant'
        MEMBER = 'MEM', 'Member'
        OFFICER = 'OFF', 'Officer'
        OWNER = 'OWN', 'Owner'

    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null = True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, blank=False, null = True)
    applicationStatement = models.CharField(max_length=1000, blank=True)
    level = models.CharField(
        max_length=3, choices=MembershipLevels.choices, default=MembershipLevels.APPLICANT)

    class Meta:
        unique_together = ('club', 'user')
        ordering = ['user']

    def __str__(self):
        return self.club.name

class Event(models.Model):
    """Event model"""
    title = models.CharField(max_length=100, blank=False)
    description = models.CharField(max_length=520, blank=False)
    date = models.DateTimeField(blank=False)
    location = models.CharField(max_length=30, blank=False)
    clubs = models.ForeignKey(Club, on_delete=models.CASCADE, blank=False)

    def getComments(self):
        return self.eventcomment_set.filter(models.Q(parent_event=self))

class Book(models.Model):
    """Book model"""

    class Meta:
        ordering = ['ISBN']

    ISBN = models.CharField(max_length=13, blank=False)
    BookTitle = models.CharField(max_length=150, blank=False)
    BookAuthor = models.CharField(max_length=150, blank=False)
    YearOfPublication = models.CharField(max_length=4, blank=False)
    Publisher = models.CharField(max_length=150, blank=False)
    ImageURLS = models.CharField(max_length=300, blank=False)
    ImageURLM = models.CharField(max_length=300, blank=False)
    ImageURLL = models.CharField(max_length=300, blank=False)

    def get_image(self):
        return self.ImageURLL

    def get_id(self):
        return self.id

    @property
    def average_rating(self):
        return UserRating.objects.aggregate(Avg('bookRating'))['rating__avg']

    def __str__(self):
        return self.BookTitle

class ClubBookAssignment(models.Model):
    """Club book assignment model"""

    class Meta:
        constraints = [models.UniqueConstraint(fields=['clubs','ISBN'], name="unique_club_book_pair")]

    clubs = models.ForeignKey(Club, on_delete=models.CASCADE, blank=False)
    ISBN = models.ForeignKey(Book, on_delete=models.CASCADE,  blank=False)


class CurrentlyViewing(models.Model):
    """Model for storing which club the user is currently viewing"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, blank=False, unique=True)
    club = models.ForeignKey(Club, on_delete=models.SET_NULL, null=True, blank=True)

    @classmethod
    def get_currently_viewing(cls, user):
        """Gets the club the user is currently viewing - if a session doesn't exist None is returned"""
        try:
            s = cls.objects.get(user=user)
            return s.club
        except ObjectDoesNotExist:
            return None

    @classmethod
    def set_currently_viewing(cls, user, club):
        """Sets the currently viewing club for a given user"""
        current = cls.get_currently_viewing(user)
        if current:
            current_session = CurrentlyViewing.objects.get(user=user.id)
            current_session.club = club
            current_session.save()
            return current_session
        else:
            s = CurrentlyViewing(user=user, club=club)
            s.save()
            return s

class CurrentlyReading(models.Model):
    """Model for storing which book the club is currently reading and setting the currently reading book for all users"""

    club = models.OneToOneField(Club, on_delete=models.SET_NULL, null=True, blank=True)
    book = models.OneToOneField(Book, on_delete=models.CASCADE, primary_key=True, blank=False)

    @classmethod
    def get_currently_reading(cls, club):
        """Gets the book the club is currently reading - if a session doesn't exist None is returned"""
        try:
            s = cls.objects.get(club=club)
            return s.book
        except ObjectDoesNotExist:
            return None

    @classmethod
    def set_currently_reading(cls, club, book):
        """Sets the currently reading book for a given club"""
        current = cls.get_currently_reading(club)
        if current:
            current_session = CurrentlyReading.objects.get(club=club.id)
            current_session.book = book
            current_session.save()
            return current_session
        else:
            s = CurrentlyReading(club=club, book=book)
            s.save()
            return s

    @classmethod
    def clear_currently_reading(cls, book):
        """ Clears the book the club is currently reading """
        try:
            s = cls.objects.get(book=book).delete()
        except ObjectDoesNotExist:
            pass

class ClubReadingList(models.Model):
    """ Model for storing all the books a club has read """

    club = models.ForeignKey(Club, on_delete=models.CASCADE, blank=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, blank=False)

    @classmethod
    def save_book_to_reading_list(cls, club, book):
        """ Saves a book to the reading list for a given club """
        try:
            book = ClubReadingList.objects.get(club=club, book=book)
        except ObjectDoesNotExist:
            reading_list = ClubReadingList(club=club, book=book)
            reading_list.save()

    @classmethod
    def get_all_books_for_club(cls, club):
        """ Gets all the books a club has read """
        try:
            reading_list = cls.objects.filter(club=club)
            get_books = []
            for book in reading_list:
                get_books.append(Book.objects.get(id=book.book.id))
            return get_books
        except ObjectDoesNotExist:
            return None

class Post(models.Model):
    """Posts by users in their club forum."""

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='club_id')
    text = models.CharField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True)

    def getComments(self):
        return self.comment_set.filter(models.Q(parent_post=self))


    class Meta:
        """Model options."""

        ordering = ['-created_at']

class Comment(models.Model):
    """Comments by users under posts in their club forum."""

    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    text = models.CharField(max_length=280, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    parent_post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=False)

    class Meta:
        """Model options."""

        ordering = ['-created_at']


class EventComment(models.Model):
    """Comments by users under events in their club calendar."""

    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    text = models.CharField(max_length=280, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    parent_event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=False)

    class Meta:
        """Model options."""

        ordering = ['-created_at']

class UserRating(models.Model):
    """Model for storing user ratings"""

    userId = models.IntegerField(blank=False)
    ISBN = models.CharField(max_length=20, blank=False)
    bookRating = models.IntegerField(blank=False)
