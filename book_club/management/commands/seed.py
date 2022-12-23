from cmath import nan
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django.contrib.auth.hashers import make_password
from faker import Faker
from book_club import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password

import random
import pandas as pd

class Command(BaseCommand):
    PASSWORD = "Password123"
    USER_COUNT = 100
    CLUB_COUNT = 15

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        user_count = 0
        club_count = 0
        users = []
        clubs = []

        # Books seed:
        start_time = timezone.now()
        file_path = "BX_Books.csv"
        x = list()
        count = 0

        bookSeedData = pd.read_csv(file_path, encoding= 'unicode_escape', sep=";", low_memory=False)

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

        # User Ratings seed:
        start_time = timezone.now()
        file_path = "BX-Book-Ratings.csv"
        x = list()
        count = 0

        ratingSeedData = pd.read_csv(file_path, encoding= 'unicode_escape', sep=";", low_memory=False)


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

        # Add BX-Users seed:
        start_time = timezone.now()
        file_path = "BX-Users.csv"

        userSeedData = pd.read_csv(file_path, encoding= 'unicode_escape', sep=";", low_memory=False)

        x = list()
        count = 0

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

            x.append(models.User(
                id = user['User-ID'],
                first_name = first_name,
                last_name = last_name,
                email = email,
                password = make_password(Command.PASSWORD, None, 'md5'),
                bio = bio,
                age = age,
                location = user['Location'],
                personal_statement = personal_statement
            ))

            count += 1
            print(f'Seeding User {count}', end='\r')

        print('Bulk adding users please wait...')
        models.User.objects.bulk_create(x)
        print(f'Adding users from csv. {models.User.objects.count()} users added.')


        end_time = timezone.now()
        self.stdout.write(
            self.style.SUCCESS(
                f"Loading CSV took: {(end_time-start_time).total_seconds()} seconds."
            )
        )

        while club_count < Command.CLUB_COUNT:
            print(f'Seeding club {club_count}', end='\r')
            try:
                clubs.append(self._create_club())
            except IntegrityError:
                continue
            club_count += 1


        try:        
            self.makeOwnerFirstSelector()
            self._create_club_with_owner_officer_member_applicant()
            self._create_posts_per_club()
        except IntegrityError:
            print("Error seeding Team Sigma Book Club, and posts for clubs!")

        print(f'Club seeding complete. {models.Club.objects.count()} clubs created.')
        print(f'Membership seeding complete. {models.Membership.objects.count()} memberships created.')
        print(f'Post seeding complete. {models.Post.objects.count()} posts created.')
        print('Finished.')

    def _email(self, first_name, last_name):
        email = f'{first_name}.{last_name}{random.randint(1, 999999999)}@example.org'
        return email

    def _create_club(self):
        clubCity = self.faker.unique.city()
        club = models.Club.objects.create(
            name=clubCity+" Book Club",
            location=clubCity,
            description=self.faker.text(),
            theme=self.faker.text()
            )

        # Add a number of random users to the club (currently 10)
        self._seedMemberships(club, 10)


        return club

    def _seedMemberships(self, club, user_count):
        membershipLevels = models.Membership.MembershipLevels.values
        # Remove Owner from possible options to make sure we do not seed duplicate Owners
        membershipLevels.remove('OWN')

        # Retrieve a number of random users to add to the club
        users_to_process = models.User.objects.order_by('?')[:user_count]

        # Make the first User the owner
        if not club.owner() and users_to_process.count() >= 1:
            models.Membership.objects.create(user=users_to_process[0], club=club, level=models.Membership.MembershipLevels.OWNER,
                                             applicationStatement=self.faker.text())
            users_to_process = users_to_process[1:]

        for user in users_to_process:
            level = random.choice(membershipLevels)
            models.Membership.objects.create(
                user=user, club=club, level=level, applicationStatement=self.faker.text())

    def makeOwnerFirstSelector(self):
        for club in models.Club.objects.all():
            club.choosing_book_id = list(models.Membership.objects.filter(club=club,level="OWN"))[0].user.id
            club.save()

    def _create_club_with_owner_officer_member_applicant(self):
        # Select the first user as the owner, officer, member and applicant
        Owner = models.Membership.objects.filter(level="OWN")[0].user
        Owner.email = 'Owner@gmail.com'
        Owner.save()
        Officer = models.Membership.objects.filter(level="OFF")[0].user
        Officer.email = 'Officer@gmail.com'
        Officer.save()
        Member = models.Membership.objects.filter(level="MEM")[0].user
        Member.email = 'Member@gmail.com'
        Member.save()
        Applicant = models.Membership.objects.filter(level="APP")[0].user
        Applicant.email= 'Applicant@gmail.com'
        Applicant.save()

        # Create a club test club
        club = models.Club.objects.create(
            name="Team Sigma Book Club",
            location="London",
            description=self.faker.text(),
            theme=self.faker.text(),
            choosing_book_id=Owner.id
        )

        # Add the users to the club via the Membership model
        models.Membership.objects.create(
            user=Owner, club=club, level=models.Membership.MembershipLevels.OWNER, applicationStatement=self.faker.text())

        models.Membership.objects.create(
            user=Officer, club=club, level=models.Membership.MembershipLevels.OFFICER, applicationStatement=self.faker.text())

        models.Membership.objects.create(
            user=Member, club=club, level=models.Membership.MembershipLevels.MEMBER, applicationStatement=self.faker.text())

        models.Membership.objects.create(
            user=Applicant, club=club, level=models.Membership.MembershipLevels.APPLICANT, applicationStatement=self.faker.text())

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