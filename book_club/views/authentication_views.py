"""Authentication related views for the clubs app."""
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.views import View

from book_club.forms import LogInForm
from book_club.models import CurrentlyViewing, Membership
from book_club.views.mixins import LoginProhibitedMixin


class LogInView(LoginProhibitedMixin, View):
    """View that handles log in."""

    http_method_names = ['get', 'post']

    def get(self, request):
        """Display log in template."""
        next = request.GET.get('next') or ''
        return self.render(next)

    def post(self, request):
        """Handle log in attempt."""
        form = LogInForm(request.POST)
        next = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
        user = form.get_user()
        if user is not None:
            login(request, user)
            self._update_currently_viewing(user)
            return redirect(next)
        messages.add_message(request, messages.ERROR, 'The username/password provided were invalid.')
        return self.render(next)

    def render(self, next):
        """Render log in template with log in form."""
        form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': next})

    def _update_currently_viewing(self, user):
        """Set the user's viewing club if none is already set."""
        if CurrentlyViewing.get_currently_viewing(user) is None:
            member_memberships = Membership.objects.filter(user=user)
            officer_memberships = Membership.objects.filter(user=user,level="OFF")
            owner_memberships =  Membership.objects.filter(user=user,level="OWN")
            membership = (member_memberships | officer_memberships | owner_memberships).first()

            if membership is not None:
                CurrentlyViewing.set_currently_viewing(user, membership.club)


def log_out(request):
    logout(request)
    return redirect('home')
