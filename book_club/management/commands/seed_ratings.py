from django.core.management.base import BaseCommand
from django.utils import timezone
from book_club import models
import pandas as pd



class Command(BaseCommand):

    def handle(self, *args, **options):
        # User Ratings seed:
        start_time = timezone.now()
        file_path = "BX-Book-Ratings.csv"
        x = list()
        count = 0

        ratingSeedData = pd.read_csv(file_path, encoding= 'latin-1', sep=";", low_memory=True)

        print("Add ratings")
        for index, rating in ratingSeedData.iterrows():
            x.append(models.UserRating(
                    userId = rating['User-ID'],
                    ISBN = rating['ISBN'],
                    bookRating = rating['Book-Rating']
            ))
            count += 1
            print(f'Seeding Rating {count}', end='\r')

        print('Bulk adding ratings please wait...')
        models.UserRating.objects.bulk_create(x)
        print(f'Adding user ratings from csv. {models.UserRating.objects.count()} ratings added.')


        end_time = timezone.now()
        self.stdout.write(
            self.style.SUCCESS(
                f"Loading CSV took: {(end_time-start_time).total_seconds()} seconds."
            )
        )
