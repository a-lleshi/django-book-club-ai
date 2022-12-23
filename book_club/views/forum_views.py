from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from book_club.forms import PostForm
from book_club.models import Club, Membership, Post, Comment
from django.contrib.auth import get_user_model

@login_required
def forum(request, club_id):
    """Display all posts for a club"""
    form = PostForm()
    current_club = Club.objects.get(id=club_id)
    posts = Post.objects.filter(club=current_club)
    return render(request, 'club_forum.html', {'club_id': club_id, 'form': form, 'posts': posts})

@login_required
def new_post(request, club_id):
    """Add a new post to the club's forum """
    current_club = Club.objects.get(id=club_id)
    if request.method == 'POST':
        if request.user.is_authenticated:
            user = request.user
            form = PostForm(request.POST)
            if form.is_valid():
                text = form.cleaned_data.get('text')
                post = Post.objects.create(author=user, text=text, club=current_club)
                return redirect('forum', club_id=club_id)
        else:
            return redirect('/login')

    return render(request, 'club_forum.html', {'form': form})

@login_required
def new_comment(request, post_id):
    """ Add a new comments under a post on club forum """
    current_post = Post.objects.get(id=post_id)
    form = PostForm()
    if request.method == 'POST':
        if request.user.is_authenticated:
            user = request.user
            form = PostForm(request.POST)
            if form.is_valid():
                text = form.cleaned_data.get('text')
                comment = Comment.objects.create(author=user, text=text, parent_post=current_post)
                return redirect('forum', club_id=current_post.club.id)
        else:
            return redirect('/login')

    return render(request, 'club_forum.html', {'form': form})
