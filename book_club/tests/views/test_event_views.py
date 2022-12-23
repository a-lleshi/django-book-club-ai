"""Unit tests for the Event list."""
from django.conf import settings
from django.test import TestCase
from book_club.models import User, Club, Membership, CurrentlyViewing, Event
from django.urls import reverse
from datetime import datetime
from django.utils.timezone import get_current_timezone

class AddEventTestCase(TestCase):
    """Unit tests for adding a new event."""

    fixtures = ['book_club/tests/fixtures/default_club.json']

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.member = Membership.objects.get(user=2, club=1).user
        self.user = User.objects.get(id='2')

        CurrentlyViewing(user=self.user, club=self.club).save()

        self.data = { 'title': 'Example Event','description': 'The quick brown fox jumps over the lazy dog.', 'date':'2022-09-01 16:00:00', 'location': 'London', 'clubs': '1' }

        self.url = reverse('add_event')

    def test_club_list_url(self):
        correct_url='/add_event/'
        self.assertEqual(self.url, correct_url)

    def test_post_new_event_redirects_when_not_logged_in(self):
        event_count_before = Event.objects.count()
        redirect_url = '/log_in/?next=/add_event/'
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url,
            status_code=302, target_status_code=200, fetch_redirect_response=True
        )
        event_count_after = Event.objects.count()
        self.assertEqual(event_count_after, event_count_before)
        self.assertTemplateUsed(response, 'log_in.html')

    def test_post_new_event_redirects_when_no_club_currently_viewing(self):
        self.client.login(email=self.user.email, password="Password123")
        CurrentlyViewing.set_currently_viewing(self.user, None)
        event_count_before = Event.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        event_count_after = Event.objects.count()
        self.assertEqual(event_count_after, event_count_before)
        self.assertTemplateUsed(response, 'add_event.html')

    def test_successful_new_event(self):
        self.client.login(email=self.user.email, password="Password123")
        event_count_before = Event.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        event_count_after = Event.objects.count()
        self.assertEqual(event_count_after, event_count_before+1)
        new_event = Event.objects.get(id = event_count_before+1)
        self.assertEqual(self.club, new_event.clubs)
        response_url = "/add_event/?submitted=True"
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'add_event.html')

    def test_unsuccessful_new_event(self):
        self.client.login(email=self.user.email, password='Password123')
        event_count_before = Event.objects.count()
        self.data['description'] = ""
        response = self.client.post(self.url, self.data, follow=True)
        event_count_after = Event.objects.count()
        self.assertEqual(event_count_after, event_count_before)
        self.assertTemplateUsed(response, 'add_event.html')


class EventListTestCase(TestCase):
    """Unit tests for the Applicant list."""

    fixtures = ['book_club/tests/fixtures/default_club.json']

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.applicant = Membership.objects.get(user=1, club=1).user
        self.member = Membership.objects.get(user=2, club=1).user
        self.officer = Membership.objects.get(user=3, club=1).user
        self.owner= Membership.objects.get(user=4, club=1).user

        self.event1 = Event.objects.create(title="Test Event 1", description="Test Description 1", date=datetime.now(tz=get_current_timezone()), location="Online", clubs=self.club)
        self.event2 = Event.objects.create(title="Test Event 2", description="Test Description 2", date=datetime.now(tz=get_current_timezone()), location="Office", clubs=self.club)

        CurrentlyViewing(user=self.member, club=self.club).save()
        CurrentlyViewing(user=self.applicant, club=self.club).save()

        self.url = reverse('event_list')

    def test_club_list_url(self):
        correct_url='/event_list/'
        self.assertEqual(self.url, correct_url)

    def test_get_event_list_view_when_logged_in(self):
        self.client.login(email= self.member, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event_list.html')

    def test_get_event_list_view_when_not_logged_in_redirects_to_log_in(self):
        response = self.client.get(self.url)
        response_url = reverse('log_in') + f"?next={self.url}"
        self.assertRedirects(response, response_url,
                             status_code=302, target_status_code=200)

    def test_event_list_displays_event_details(self):
        self.client.login(email=self.member.email, password='Password123')
        url = reverse('event_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event_list.html')
        self.assertContains(response, f'{self.event1.title}')
        self.assertContains(response, f'{self.event1.description}')
        self.assertContains(response, f'{self.event1.location}')
        self.assertContains(response, f'{self.event2.title}')
        self.assertContains(response, f'{self.event2.description}')
        self.assertContains(response, f'{self.event2.location}')

    def test_get_event_list_as_member(self):
        self.client.login(email=self.member.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event_list.html')

    def test_get_event_list_as_applicant(self):
        self.client.login(email=self.applicant.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event_list.html')

    def test_get_event_list_as_officer(self):
        self.client.login(email=self.officer.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event_list.html')

    def test_get_event_list_as_owner(self):
        self.client.login(email=self.owner.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event_list.html')
