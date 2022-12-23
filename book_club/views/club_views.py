from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from book_club.forms import ClubForm, EditClubForm
from book_club.models import Club, Membership, CurrentlyViewing, User, ClubBookAssignment, UserRating
from django.core.exceptions import ObjectDoesNotExist
from book_club.tests.helpers import owner_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from book_club.filters import UserFilter,ClubFilter
from book_club.views import FilteredListView
from django.conf import settings

@login_required
def create_club(request):
    submitted = False
    form = ClubForm
    if request.method == 'POST':
        user = request.user
        if user is not None:
            form = ClubForm(request.POST)
            if form.is_valid():
                club = form.save(user)
                CurrentlyViewing.set_currently_viewing(request.user, club)
                return HttpResponseRedirect('/club/create?submitted=True')
        else:
            return HttpResponseRedirect('/login')

    else:
        if 'submitted' in request.GET:
            submitted = True

    return render(request, 'clubs/create.html', {'form': form, 'submitted': submitted})


class ClubListView(LoginRequiredMixin, FilteredListView):
    """A view for showing all clubs in the system"""
    model = Club
    filterset_class = ClubFilter
    paginate_by = settings.CLUBS_PER_PAGE
    template_name = 'club_list.html'
    context_object_name = 'club_list'

    def get_queryset(self, new_qs=None):
        clubs = Club.objects.all()
        return super().get_queryset(clubs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        self.current_club = CurrentlyViewing.get_currently_viewing(self.request.user)
        club = CurrentlyViewing.get_currently_viewing(self.request.user)
        context['clubs_applicants'] = Membership.objects.filter(club=self.current_club.id,level="APP").prefetch_related('user') if club else None
        return context


class MemberListView(LoginRequiredMixin, FilteredListView):
    """A view for showing members in a current club"""
    model = User
    filterset_class = UserFilter
    paginate_by = settings.USERS_PER_PAGE
    template_name = 'club_member_list.html'
    context_object_name = 'members'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        self.current_club = CurrentlyViewing.get_currently_viewing(self.request.user)
        self.userExistsInClub = Membership.objects.filter(user=request.user.id,club=self.current_club.id).exists()
        if self.current_club and  Membership.objects.filter(user=request.user.id,club=self.current_club.id).exists():
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('dashboard')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['exists_in_club'] =  self.userExistsInClub
        context['current_club'] = self.current_club
        context['request_is_owner'] = Membership.objects.filter(user = self.request.user, club=self.current_club.id,level="OWN").exists()
        return context

    def get_queryset(self, new_qs=None):
        club_users = Membership.objects.filter(club=self.current_club.id).prefetch_related('user')
        return super().get_queryset(club_users)


@login_required
def show_club(request, club_id):

    reqUser = request.user
    current_club = Club.objects.get(id=club_id)

    try:
       membership = Membership.objects.get(club=current_club, user=request.user)
       level = membership.level
    except ObjectDoesNotExist:
       level = ''

    try:
       clubBooks = ClubBookAssignment.objects.filter(clubs=current_club).prefetch_related('ISBN')
    except ObjectDoesNotExist:
       clubBooks = ''

    # get all the books that the logged in user has already rated and add them to the array with the values
    try:
       userRatedBooks = UserRating.objects.filter(userId=reqUser.id).values('ISBN', 'bookRating')
    except ObjectDoesNotExist:
       userRatedBooks = []

    return render(request, 'show_club.html', {'current_user': request.user, 'current_club': current_club, 'membership_level': level, 'club_books': clubBooks, 'userRatedBooks': list(userRatedBooks)})


@login_required
@owner_required
def club_member_promote(request, club_id, userid, action):

    if(CurrentlyViewing.objects.get(user=request.user).club== Club.objects.get(id = club_id)):
        try:
            current_membership = Membership.objects.get(user=userid, club=club_id)
            current_membership.level = 'OFF'
            current_membership.save()
        except ObjectDoesNotExist:
            redirect('club_member_list')
        return redirect('club_member_list')
    else:
        redirect('club_member_list')



@login_required
@owner_required
def club_member_demote(request, club_id, userid):

    if(CurrentlyViewing.objects.get(user=request.user).club== Club.objects.get(id = club_id)):
        try:
            current_membership = Membership.objects.get(user=userid, club=club_id)
            current_membership.level = 'MEM'
            current_membership.save()
        except ObjectDoesNotExist:
            redirect('club_member_list')
        return redirect('club_member_list')
    else:
        redirect('club_member_list')


@login_required
def edit_club(request, club_id):
    current_club = Club.objects.get(id=club_id)
    if request.method == 'POST':
        form = EditClubForm(instance=current_club, data=request.POST)
        if form.is_valid():
            messages.add_message(request, messages.SUCCESS, "Updated successfully!")
            form.save()
            return redirect('show_club', club_id=club_id)
    else:
        form = EditClubForm(instance=current_club)
    return render(request, 'edit_club.html', {'form':form, 'current_club': current_club})

@login_required
def switch_club(request, club_name):
    """A view for changing the currently displayed/selected club """
    try:
        new_club = Club.objects.get(name=club_name)
        if Membership.objects.get(club=new_club, user=request.user):
            CurrentlyViewing.set_currently_viewing(request.user, new_club)
        return redirect('dashboard')
    except ObjectDoesNotExist:
        return redirect('dashboard')


def member_id(request, memberid, club_id):
    """Display more info about a member of a club"""
    Member = get_user_model()
    members = Member.objects.filter(id=memberid)

    allMemberships = Membership.objects.filter(user=memberid)
    qclub = Club.objects.filter(id=club_id)
    qMembership = Membership.objects.filter(user=memberid,club=club_id).first()
    qclubID = qclub.first()

    if members:
        return render(request, 'memberprofile.html', {'members': members, 'club': qclub, 'qMembership': qMembership, 'qclub': qclubID, 'allMemberships': allMemberships})
    else:
        return redirect('home')
