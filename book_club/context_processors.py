from .models import Club, CurrentlyViewing,Membership,UserRating,User
from django.template.defaulttags import register
from django import template
from django.db.models import Avg

def club_info(request):
    """ Often used info for templates"""
    if request.user.is_authenticated:
        club = CurrentlyViewing.get_currently_viewing(request.user)
        clubs = Membership.objects.filter(user=request.user)
        if club is not None:
            return {
                'club_user': {
                    'is_owner': club.owner() == request.user,
                    'is_officer': club.getAdministrators().filter(user=request.user).exists(),
                    'is_member': club.getMembers().filter(user=request.user).exists(),
                    'is_applicant' : club.getApplicants().filter(user=request.user).exists(),
                },
                'user_choosing_book': Club.objects.filter(id=club.id, choosing_book_id=request.user.id).exists(),
                'name_of_book_chooser': User.objects.get(id = club.choosing_book_id),
                'current_club_id':  club.id,
                'current_club': club,
                'user_clubs': clubs
            }
    return {}
