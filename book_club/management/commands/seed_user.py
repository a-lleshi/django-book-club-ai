from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from book_club import models
from faker import Faker

import random
import pandas as pd


class Command(BaseCommand):
    PASSWORD = "Password123"

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):

        # Add BX-Users seed:
        start_time = timezone.now()
        file_path = "BX-Users.csv"
        
        userSeedData = pd.read_csv(file_path, encoding= 'latin-1', sep=";", low_memory=False)
        
        x = list()
        count = 0
        print('Test')
        for index, user in userSeedData.iterrows():
        
            first_name = self.faker.first_name()
            last_name = self.faker.last_name()
            email = self._email(first_name, last_name)
            bio = self.faker.text(max_nb_chars=520)
            personal_statement = self.faker.text(max_nb_chars=520)
            age = user['Age']
        
            if (age == "NULL" or "NaN" or "nan" or "None" or "none" or "null"):
                age = random.randint(10, 150)
            else:
                age = int(user['Age'])
        
            models.User.objects.create(
                id = user['User-ID'],
                first_name = first_name,
                last_name = last_name,
                email = email,
                password = make_password(Command.PASSWORD, None, 'md5'),
                bio = bio,
                age = age,
                location = user['Location'],
                personal_statement = personal_statement
            )
        
            count += 1
            print(f'Seeding User {count}', end='\r')
        
        print('Bulk adding users please wait...')
        #models.User.objects.bulk_create(x)
        print(f'Adding users from csv. {models.User.objects.count()} users added.')


        end_time = timezone.now()
        self.stdout.write(
            self.style.SUCCESS(
                f"Loading CSV took: {(end_time-start_time).total_seconds()} seconds."
            )
        )
    
    def _email(self, first_name, last_name):
        email = f'{first_name}.{last_name}{random.randint(1, 999999999)}@example.org'
        return email