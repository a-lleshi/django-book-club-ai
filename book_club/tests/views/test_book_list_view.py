from django.test import TestCase
from django.urls import reverse
from book_club.models import User, Book
from book_club.tests.helpers import LogInRequiredTests, _create_test_books
from django.conf import settings


class ClubInfoViewTestCase(TestCase, LogInRequiredTests):
    """Tests for the club info view."""

    fixtures = [

        'book_club/tests/fixtures/default_user.json',
        'book_club/tests/fixtures/second_user.json',
        'book_club/tests/fixtures/books.json'

    ]

    def setUp(self):
        self.book1 = Book.objects.get(pk=1)
        self.book2 = Book.objects.get(pk=2)
        self.url = reverse('book_list')
        self.url_string = '/book_list/'
        self.template_name = 'book_list.html'
        self.user = User.objects.get(email='johndoe@example.com')

    def test_book_list_url(self):
        self.assertEqual(self.url, '/book_list/')

    def test_get_book_list(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_list.html')

    def test_get_club_list_shows_all_clubs(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        books = list(response.context['page_obj'])
        self.assertEqual(books, [self.book2, self.book1])
        self.assertContains(response, self.book1.ISBN)
        self.assertContains(response, self.book1.BookTitle)
        self.assertContains(response, self.book1.BookAuthor)
        self.assertContains(response, self.book1.YearOfPublication)
        self.assertContains(response, self.book1.ImageURLS)
        self.assertContains(response, self.book1.ImageURLM)
        self.assertContains(response, self.book1.ImageURLL)
        self.assertContains(response, self.book2.ISBN)
        self.assertContains(response, self.book2.BookTitle)
        self.assertContains(response, self.book2.BookAuthor)
        self.assertContains(response, self.book2.YearOfPublication)
        self.assertContains(response, self.book2.ImageURLS)
        self.assertContains(response, self.book2.ImageURLM)
        self.assertContains(response, self.book2.ImageURLL)

    def test_successful_search_suiting_both(self):
        self.client.login(email=self.user.email, password='Password123')
        url = self.url + "?BookAuthor=Christopher+Biffle"
        response = self.client.get(url)
        filtered_book_list = list(response.context['page_obj'])
        self.assertEqual(len(filtered_book_list), 2)

    def test_successful_search_suiting_one(self):
        self.client.login(email=self.user.email, password='Password123')
        url = self.url + "?BookTitle=Amazing"
        response = self.client.get(url)
        filtered_book_list = list(response.context['page_obj'])
        self.assertEqual(len(filtered_book_list), 1)

    def test_unsuccessful_more_details_request(self):
        self.client.login(email=self.user.email, password='Password123')
        url = self.url + "more_details/000000"
        response = self.client.get(url)
        response_url = reverse('book_list')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        

    def test_book_list_with_pagination(self):
        books = _create_test_books(self, self.user, 16)
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(len(response.context['page_obj']), 6)
        self.assertTrue(response.context['is_paginated'])
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_one_url = self.url + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(len(response.context['page_obj']), 6)
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_two_url = self.url + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(len(response.context['page_obj']), 6)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_three_url = self.url + '?page=3'
        response = self.client.get(page_three_url)
        self.assertEqual(len(response.context['page_obj']), 6)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertFalse(page_obj.has_next())
