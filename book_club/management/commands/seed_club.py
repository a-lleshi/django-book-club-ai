from django.core.management.base import BaseCommand
from book_club import models
from django.db.utils import IntegrityError
from faker import Faker


import random
import pandas as pd

class Command(BaseCommand):
    CLUB_COUNT = 15

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        club_count = 0
        clubs = []

        while club_count < Command.CLUB_COUNT:
            print(f'Seeding club {club_count}', end='\r')
            try:
                clubs.append(self._create_club())
            except IntegrityError:
                continue
            club_count += 1
        
        
        self.makeOwnerFirstSelector()
        self._create_club_with_owner_officer_member_applicant()
        
        print(f'Club seeding complete. {models.Club.objects.count()} clubs created.')
        print(f'Membership seeding complete. {models.Membership.objects.count()} memberships created.')
        print('Finished.')
    
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