from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from book_club.forms import EventForm, PostForm
from book_club.models import Event, CurrentlyViewing, EventComment

@login_required
def add_event(request):
    current_club = CurrentlyViewing.get_currently_viewing(request.user)

    if current_club == None:
        messages.add_message(request, messages.ERROR, 'Please select a club in the top right or join a club!')
        return render(request, 'add_event.html')
    else:
        submitted = False
        if request.method == 'POST':
            form = EventForm(current_club, request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/add_event?submitted=True')
        else:
            form = EventForm(current_club)
            if 'submitted' in request.GET:
                submitted = True

        return render(request, 'add_event.html', {'form': form, 'submitted': submitted})

@login_required
def new_event_comment(request, event_id):
    """Creating new comments under events"""
    current_event = Event.objects.get(id=event_id)
    form = PostForm()
    if request.method == 'POST':
        user = request.user
        form = PostForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data.get('text')
            comment = EventComment.objects.create(author=user, text=text, parent_event=current_event)
            return redirect('event_list')

    return render(request, 'event_list.html', {'form': form})

@login_required
def all_events(request):
    """Display all events in a club"""
    form = PostForm()
    current_club = CurrentlyViewing.get_currently_viewing(request.user)
    if current_club == None:
        messages.add_message(request, messages.ERROR, 'Please select a club in the top right or join a club!')
        return render(request, 'event_list.html')
    else:
        event_list = Event.objects.filter(clubs_id=current_club.id)
        return render(request, 'event_list.html', {
            'event_list': event_list,
            'form': form
        })
