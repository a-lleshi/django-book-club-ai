from django.test import TestCase
from django.urls import reverse
from book_club.models import User, Book, Club, Membership, CurrentlyViewing, CurrentlyReading, UserRating, ClubReadingList
from book_club.tests.helpers import LogInRequiredTests
from django.conf import settings


class BookRecommendationTestCase(TestCase, LogInRequiredTests):
    """Tests for the club info view."""

    fixtures = [
        'book_club/tests/fixtures/books.json',
        'book_club/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        self.url = reverse('recommendation')
        self.url_string = '/recommendation/'
        self.template_name = 'recommended_user_books.html'
        self.book1 = Book.objects.get(pk=1)
        self.book2 = Book.objects.get(pk=2)
        self.club = Club.objects.get(name='Horror Club')
        self.user = User.objects.get(pk=1) #Membership.objects.get(user=1, club=1).user
        self.user2 = User.objects.get(pk=2) #Membership.objects.get(user=2, club=1).user
        self.session = CurrentlyViewing.set_currently_viewing(self.user, self.club)
        self.rating = UserRating.objects.create(
            userId = self.user.id,
            ISBN = self.book1.ISBN,
            bookRating = 3,
        )
        self.rating2 = UserRating.objects.create(
            userId = self.user.id,
            ISBN = self.book2.ISBN,
            bookRating = 5,
        )
        self.rating3 = UserRating.objects.create(
            userId = self.user2.id,
            ISBN = self.book1.ISBN,
            bookRating = 4,
        )
        self.url2 = reverse('set_reading',kwargs={'book_id':self.book1.id})
        self.url3 = reverse('clear_book_add_book',kwargs={'book_id':self.book1.id})

    # def test_get_recommendations_without_selected_club_redirects(self):
    #     self.client.login(email=self.user.email, password='Password123')
    #     session = CurrentlyViewing.set_currently_viewing(self.user, None)
    #     response = self.client.get(self.url)
    #     redirect_url = reverse('club_readings')
    #     self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_recommendations_with_a_book_already_assigned(self):
        self.client.login(email=self.user.email, password='Password123')
        self.currReading = CurrentlyReading.set_currently_reading(self.club, self.book1)
        response = self.client.get(self.url)
        redirect_url = reverse('club_readings')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_recommendations_when_assigned(self):
        self.client.login(email=self.user.email, password='Password123')
        self.club.choosing_book = self.user
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)

    def test_get_recommendations_when_not_assigned_to_select(self):
        session2 = CurrentlyViewing.set_currently_viewing(self.user2, self.club)
        self.client.login(email=self.user2.email, password='Password123')
        response = self.client.get(self.url)
        redirect_url = reverse('club_readings')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_set_reading_recommended_book(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url2)
        current_reading_in_club = CurrentlyReading.objects.get(club_id=self.club)
        self.assertEquals(self.book1,current_reading_in_club.book)
        redirect_url = reverse('club_readings')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_set_reading_recommended_book_without_currently_viewing(self):
        self.client.login(email=self.user2.email, password='Password123')
        response = self.client.get(self.url2)
        current_reading_in_club = CurrentlyReading.objects.filter(club_id=self.club).exists()
        self.assertEquals(False,current_reading_in_club)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_currently_reading_recommended_book(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url2)
        current_reading_in_club = CurrentlyReading.objects.get(club_id=self.club)
        self.assertEquals(self.book1,current_reading_in_club.book)
        redirect_url = reverse('club_readings')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_clear_book_add_book(self):
        self.client.login(email=self.user.email, password='Password123')
        club_past_reading_list_length_before = len(ClubReadingList.get_all_books_for_club(self.club))
        response = self.client.get(self.url2)
        current_reading_in_club = CurrentlyReading.objects.get(club_id=self.club)
        self.assertEquals(self.book1,current_reading_in_club.book)
        redirect_url = reverse('club_readings')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        response_after_cleared = response = self.client.get(self.url3)
        redirect_url = reverse('club_readings')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        club_past_reading_list_length_after_deletion = len(ClubReadingList.get_all_books_for_club(self.club))
        self.assertEquals(club_past_reading_list_length_before,club_past_reading_list_length_after_deletion-1)
