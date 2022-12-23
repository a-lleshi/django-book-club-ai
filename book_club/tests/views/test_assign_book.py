"""Unit tests for assigning a book."""
from django.conf import settings
from django.test import TestCase
from book_club.models import User, Club, Membership, CurrentlyViewing, Book, UserRating, ClubBookAssignment
from django.urls import reverse


class AssignBookTestCase(TestCase):
    """Unit tests for assigning books."""

    fixtures = [
        'book_club/tests/fixtures/default_club.json',
        'book_club/tests/fixtures/books.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.owner = User.objects.get(pk=4)
        self.book1 = Book.objects.get(pk=1)
        CurrentlyViewing(user=self.owner, club=self.club).save()
        self.url = reverse('assign_book', kwargs={'club_id': self.club.id, 'book_isbn': self.book1.ISBN})
        self.url2 = reverse('delete_assign_book', kwargs={'club_id': self.club.id, 'book_isbn': self.book1.ISBN})
        self.url3 = reverse('assign_book', kwargs={'club_id': self.club.id, 'book_isbn': "999999999999999999"})

    def test_rate_book_url(self):
        correct_url = f'/book_list/1/0767409752'
        self.assertEqual(self.url, correct_url)

    def test_check_book_assignment_object(self):
        self.client.login(email=self.owner.email, password='Password123')
        response = self.client.post(self.url, follow = True)
        doesAssignedBookExist = ClubBookAssignment.objects.get(clubs = self.club ,ISBN=self.book1)
        self.assertEqual(doesAssignedBookExist.ISBN, self.book1)
        self.assertEqual(doesAssignedBookExist.clubs, self.club)

    def test_check_book_assignment_removed(self):
        self.client.login(email=self.owner.email, password='Password123')
        response = self.client.post(self.url, follow = True)
        doesAssignedBookExist = ClubBookAssignment.objects.get(clubs = self.club ,ISBN=self.book1)
        self.assertEqual(doesAssignedBookExist.ISBN, self.book1)
        self.assertEqual(doesAssignedBookExist.clubs, self.club)
        response_after_delete = self.client.post(self.url2, follow = True)
        doesAssignedBookExist = ClubBookAssignment.objects.filter(clubs = self.club ,ISBN=self.book1).exists()
        self.assertEqual(doesAssignedBookExist, False)
        self.assertEqual(doesAssignedBookExist, False)

    def test_check_book_assignment_when_doesnt_exist(self):
        self.client.login(email=self.owner.email, password='Password123')
        response = self.client.post(self.url3, follow = True)
        response_url = reverse('book_list_club',kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_check_book_assignment_removed_when_doesnt_exist(self):
        self.client.login(email=self.owner.email, password='Password123')
        response = self.client.post(self.url2, follow = True)
        response_url = reverse('book_list_club',kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
