from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from book_club.models import User, Club, Membership, Book, UserRating, Post


def unseed_users():
    User.objects.filter(is_staff=False, is_superuser=False).delete()

def unseed_clubs():
    Club.objects.all().delete()

def unseed_memberships():
    Membership.objects.all().delete()

def unseed_books():
    Book.objects.all().delete()

def unseed_user_ratings():
    UserRating.objects.all().delete()

def unseed_posts():
    Post.objects.all().delete()

class Command(BaseCommand):
    def handle(self, *args, **options):
        unseed_users()
        unseed_memberships()
        unseed_clubs()
        unseed_books()
        unseed_user_ratings()
        unseed_posts()
