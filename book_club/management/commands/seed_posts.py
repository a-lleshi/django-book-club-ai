from django.core.management.base import BaseCommand
from book_club import models
from django.db.utils import IntegrityError
from faker import Faker


import random
import pandas as pd

class Command(BaseCommand):
    post_per_club = 5

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):

        try:
            self._create_posts_per_club()
        except IntegrityError:
            print("Error seeding posts")
 
    def _create_posts_per_club(self):
        for club in models.Club.objects.all():
            for i in range(0,5):
                author = list(models.Membership.objects.filter(club=club,level__in=["MEM","OFF","OWN"]))

                models.Post.objects.create(
                    club=club,
                    text=self.faker.text(max_nb_chars=250),
                    author=author[random.randint(0,len(author)-1)].user,
                    created_at=self.faker.date_time_between(start_date="-1y", end_date="now", tzinfo=None)
                )

                i+=1
