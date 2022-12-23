"""book club URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django import views
from django.contrib import admin
from django.urls import path
from book_club import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('event_list/', views.all_events, name='event_list'),
    path('club_list/', views.ClubListView.as_view(), name='club_list'),
    path('book_list/', views.BookListView.as_view(), name='book_list'),
    path('applicant_list/', views.ApplicantListView.as_view(), name='applicant_list'),
    path('accept_applicant/club=<int:club_id>&user=<int:user_id>', views.accept_applicant, name='accept_applicant'),
    path('reject_applicant/<int:club_id>&<int:user_id>', views.reject_applicant, name='reject_applicant'),
    path('add_event/', views.add_event, name='add_event'),
    path('club/create/', views.create_club, name='club.create'),
    path('profile/change_profile/', views.ProfileUpdateView.as_view(), name='change_profile'),
    path('profile/change_password/', views.PasswordView.as_view(), name='change_password'),
    path('member_list/', views.MemberListView.as_view(), name = 'club_member_list'),
    path('show_club/<int:club_id>', views.show_club, name='show_club'),
    path('join/<int:club_id>', views.join_club, name='join'),
    path('edit_club/<int:club_id>', views.edit_club, name='edit_club'),
    path('switch_club/<str:club_name>', views.switch_club, name='switch_club'),
    path('forum/<int:club_id>', views.forum, name='forum'),
    path('new_post/<int:club_id>', views.new_post, name='new_post'),
    path('new_comment/<int:post_id>', views.new_comment, name='new_comment'),
    path('new_event_comment/<int:event_id>', views.new_event_comment, name='new_event_comment'),
    path('member_list/<club_id>/<userid>', views.club_member_demote, name = 'club_member_demote'),
    path('member_list/<club_id>/<userid>/<str:action>/', views.club_member_promote, name = 'club_member_promote'),
    path('member_list/member/<int:club_id>/<memberid>', views.member_id, name = 'member_info'),
    path('recommendation/', views.gen_book_recommendation_for_club, name='recommendation'),
    path('set_reading/<int:book_id>', views.set_reading, name='set_reading'),
    path('club_readings/', views.get_club_current_reading, name='club_readings'),
    path('clear_book_add_book/<int:book_id>', views.clear_book_add_book, name='clear_book_add_book'),
    path('book_list/<int:club_id>', views.BookListViewAssignClass.as_view(), name='book_list_club'),
    path('book_list/<int:club_id>/<str:book_isbn>', views.BookListViewAssign, name='assign_book'),
    path('dashboard/<str:book_id>/<int:user_rating>', views.RateBookSC, name='sc_rate_book'),
    path('club_readings/<str:book_id>/<int:user_rating>', views.RateBookCR, name='cr_rate_book'),
    path('book_list/more_details/<str:book_isbn>', views.BookListMoreDetails, name='more_details'),
    path('book_list/more_details/<str:book_id>/<int:user_rating>', views.RateBookBL, name='bl_rate_book'),
    path('book_list/<int:club_id>/<str:book_isbn>/delete', views.BookListViewAssignDelete, name='delete_assign_book'),

]
