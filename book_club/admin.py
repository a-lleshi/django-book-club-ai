from django.contrib import admin
from .models import User, Membership, Club,CurrentlyViewing, Book, ClubBookAssignment, UserRating


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for users."""

    list_display = [
        'id','first_name', 'last_name', 'email', 'age','location','is_active',
    ]

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for memberships."""

    list_display = [
        'user', 'club', 'level',
    ]

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for clubs."""

    list_display = [
        'name','location','description','theme'
    ]

@admin.register(CurrentlyViewing)
class CurrentlyViewingAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for CurrentlyViewing."""

    list_display = [
        'user','club'
    ]

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for Book."""

    list_display = [
        'BookTitle','BookAuthor','ISBN','YearOfPublication'
    ]

@admin.register(ClubBookAssignment)
class ClubBookAssignmentAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for ClubBookAssignment."""

    list_display = [
        'clubs', 'ISBN'
    ]

@admin.register(UserRating)
class UserRatingAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for UserRatings."""

    list_display = [
        'userId', 'ISBN', 'bookRating'
    ]