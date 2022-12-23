from django.core.management.base import BaseCommand
from django.utils import timezone
import pandas as pd

from book_club import models


class Command(BaseCommand):

    def handle(self, *args, **options):
        # Books seed:
        start_time = timezone.now()
        file_path = "BX_Books.csv"
        x = list()
        count = 0
        
        bookSeedData = pd.read_csv(file_path, encoding= 'latin-1', sep=";", low_memory=False)
        
        print("Add books")
        for index, book in bookSeedData.iterrows():
            x.append(models.Book(
                    ISBN = book['ISBN'],
                    BookTitle = book['BookTitle'],
                    BookAuthor = book['BookAuthor'],
                    YearOfPublication = book['YearOfPublication'],
                    Publisher = book['Publisher'],
                    ImageURLS = book['ImageURLS'],
                    ImageURLM = book['ImageURLM'],
                    ImageURLL = book['ImageURLL']
            ))
            count += 1
            print(f'Seeding Book {count}', end='\r')
        
        print('Bulk adding books please wait...')
        models.Book.objects.bulk_create(x)
        print(f'Adding books from csv. {models.Book.objects.count()} books added.')
        
        
        end_time = timezone.now()
        self.stdout.write(
            self.style.SUCCESS(
                f"Loading CSV took: {(end_time-start_time).total_seconds()} seconds."
            )
        )