""" Views for a book recommendation system """
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from book_club.models import CurrentlyReading, CurrentlyViewing
from django.views.decorators.vary import vary_on_cookie
from django.views.decorators.cache import cache_page
from book_club.util.RecommenderSystem import *
from book_club.util.RecommenderEngine import *

def get_current_club(request):
    current_club = CurrentlyViewing.get_currently_viewing(request.user)
    if current_club is None:
        return None
    return current_club


def _get_club_recommendations(request):
    """ Get recommendations for a user asynchronously """
    current_club = get_current_club(request)
    club_id = current_club.id
    return getTopNRecs(club_id)

@login_required
# @cache_page(60 * 60 * 24)
# @vary_on_cookie
def gen_book_recommendation_for_club(request):
    """ Generates a book recommendation """
    current_club = CurrentlyViewing.get_currently_viewing(request.user)
    if current_club is None:
        messages.warning(request, 'You are not currently not selected a club! Recommendations will not run!')
        redirect('dashboard')

    currently_reading = CurrentlyReading.get_currently_reading(current_club)
    if currently_reading is None:
        # Get current user and check if they are in choosing_book for their club
        current_user = request.user
        choosing_book_id = current_club.choosing_book_id

        if current_user.id == choosing_book_id:
            # Get recommendations for the club
            print("Started generating book recommendation")
            start_time = timezone.now()
            reading_list = _get_club_recommendations(request)

            end_time = timezone.now()
            print(f"Loading Data: {(end_time-start_time).total_seconds()} seconds.")

            messages.success(request, f'Your reading list has been generated!')
            return render(request, 'recommended_user_books.html', {'recommended_list': reading_list,
                'current_club': current_club
            })

        else:
            messages.warning(request, 'You are not currently selected to select a book! Recommendations will not run!')
            return redirect('club_readings')

    messages.warning(request, 'Your club is currently reading a book, you will be redirected to the club reading list!')
    return redirect('club_readings')


# def _get_recommendations_for_user(user_id):
#     """ Get recommendations for a user asynchronously """
#     return get_reading_list(user_id)

# @login_required
# # @cache_page(60 * 60 * 24)
# # @vary_on_cookie
# def gen_book_recommendation_for_user(request):
#     """ Generates a book recommendation for user"""
#     print("Started generating book recommendation")
#     start_time = timezone.now()
#     example_reading_list = _get_recommendations_for_user(request.user.id)
#     for book, rating, url, book_id in example_reading_list:
#         print(f'{book_id}: {book}: {rating}: {url}')

#     end_time = timezone.now()
#     print(f"Loading Data: {(end_time-start_time).total_seconds()} seconds.")
#     return render(request, 'recommended_user_books.html', {'recommended_list': example_reading_list,})

