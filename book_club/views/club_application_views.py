from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from book_club.forms import ApplicationForm
from book_club.models import Club, Membership, CurrentlyViewing, User
from django.core.exceptions import ObjectDoesNotExist
from book_club.tests.helpers import owner_required, no_membership_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from book_club.filters import UserFilter
from book_club.views import FilteredListView
from django.conf import settings


@login_required
@no_membership_required
def join_club(request, club_id):
    """View for applying to a club"""
    form = ApplicationForm
    application_statement = ''
    if request.method == 'POST':
        user = request.user
        if user is not None:
            current_club = Club.objects.get(id=club_id)
            form =  ApplicationForm(request.POST, user=user, club=current_club)
            if form.is_valid():
                statement = form.cleaned_data['applicationStatement']
                try:
                    membership = Membership.objects.get(club=current_club, user=user)
                except ObjectDoesNotExist:
                    membership = Membership.objects.create(user=user, club=current_club, applicationStatement=statement, level='APP')
                return redirect('club_list')
        else:
            return HttpResponseRedirect('/login')
    else:
        form = ApplicationForm()
    return render(request, 'apply.html', {'form': form, 'club_id': club_id,
                    'application_statement': application_statement})


@login_required
@owner_required
def accept_applicant(request, club_id, user_id):
    """View for accepting applicants to a club from applicant list"""
    try:
        current_applicant = Membership.objects.get(user=user_id, club=club_id)
        current_applicant.level = 'MEM'
        current_applicant.save()
    except ObjectDoesNotExist:
        current_applicant = None
    return redirect('applicant_list')

@login_required
@owner_required
def reject_applicant(request, club_id, user_id):
    """View for rejecting applicants from applicant list"""
    try:
        current_applicant = Membership.objects.get(user=user_id, club=club_id)
        current_applicant.delete()
    except ObjectDoesNotExist:
        current_applicant = None
    return redirect('applicant_list')

class ApplicantListView(LoginRequiredMixin, FilteredListView):
    """A view for showing applicants in a current club"""
    model = User
    filterset_class = UserFilter
    paginate_by = settings.USERS_PER_PAGE
    template_name = 'applicant_list.html'
    context_object_name = 'applications'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        self.current_club = CurrentlyViewing.get_currently_viewing(self.request.user)
        self.userExistsInClub = Membership.objects.filter(user=request.user.id,club=self.current_club.id).exists()
        if self.current_club and  Membership.objects.filter(user=request.user.id,club=self.current_club.id).exists() and self.current_club.getAdministrators().filter(user=request.user.id).exists():
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('dashboard')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['current_club'] = self.current_club
        return context

    def get_queryset(self, new_qs=None):
        applications =Membership.objects.filter(club=self.current_club.id,level='APP').prefetch_related('user')
        return super().get_queryset(applications)
