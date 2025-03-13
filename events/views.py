from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from events.forms import EventForm, CategoryForm
from events.models import Event, Category
from django.db.models import Q, Count
from django.utils.dateparse import parse_date
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test, login_required, permission_required
from users.views import is_admin
from django.core.mail import send_mail
from django.conf import settings

def is_organizer(user):
    return user.groups.filter(name='Organizer').exists()

def is_participant(user):
    return user.groups.filter(name='Participant').exists()

def home(request):
    upcoming_events = (
        Event.objects.prefetch_related('participant')
        .select_related('category')
        .filter(date__gte=timezone.now())
        .order_by('date')
        .annotate(participant_num=Count("participant"))
    ).order_by('?')[:6]
    context = {
        "upcoming_events": upcoming_events,
        "user": request.user,
        "is_participant": request.user.groups.filter(name='Participant').exists() if request.user.is_authenticated else False,
        "is_organizer": request.user.groups.filter(name='Organizer').exists() if request.user.is_authenticated else False,
        "is_admin": request.user.groups.filter(name='Admin').exists() if request.user.is_authenticated else False,
    }
    return render(request, "homepage.html", context)

@login_required
@user_passes_test(is_organizer, login_url='no-permission')
def create_event(request):
    event_form = EventForm()
    if request.method == 'POST':
        event_form = EventForm(request.POST)
        if event_form.is_valid():
            try:
                event = event_form.save(commit=False)
                event.organizer = request.user
                event.save()
                event_form.save_m2m()
                messages.success(request, "Event created Successfully")
                return redirect('create_event')
            except Exception as e:
                messages.error(request, f"Error creating event: {str(e)}")
        else:
            messages.error(request, "Please correct the errors in the form.")
    context = {
        "event_form": event_form,
        "is_organizer": request.user.groups.filter(name='Organizer').exists() if request.user.is_authenticated else False,
    }
    return render(request, "create_event.html", context)

@login_required
@user_passes_test(is_organizer, login_url='no-permission')
def dashboard(request):
    type = request.GET.get('type', 'all')
    base_query = Event.objects.filter(organizer=request.user).select_related('category').prefetch_related('participant')
    
    # Aggregated counts for stats
    counts = base_query.aggregate(
        total_participants=Count('participant', distinct=True),
        total_events=Count('id', distinct=True),
        upcoming_events=Count('id', filter=Q(date__gt=timezone.now()), distinct=True),
        past_events=Count('id', filter=Q(date__lt=timezone.now()), distinct=True)
    )

    # Fetch filtered events with participant counts
    if type == 'upcoming':
        events = base_query.filter(date__gt=timezone.now())
    elif type == 'past':
        events = base_query.filter(date__lt=timezone.now())
    else:
        events = base_query
    events = events.annotate(participant_count=Count('participant')).order_by('date')

    # Fetch all categories with event counts (use 'event' instead of 'events')
    categories = Category.objects.annotate(event_count=Count('event', filter=Q(event__organizer=request.user)))

    context = {
        "counts": counts,
        "events": events,
        "categories": categories,
        "user": request.user,
        "current_type": type,  # To highlight the active tab
    }
    return render(request, "dashboard.html", context)

def view_events(request):
    type = request.GET.get('type', 'All')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    events = (
        Event.objects.prefetch_related('participant')
        .select_related('category')
        .annotate(participant_num=Count("participant"))
    )
    
    search = request.GET.get('search', '')
    if search:
        events = events.filter(
            Q(name__icontains=search) |
            Q(location__icontains=search)
        )

    if type != 'All':
        events = events.filter(category__name=type)

    if start_date and end_date:
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)
        if start_date and end_date:
            events = events.filter(date__range=[start_date, end_date])

    categories = Event.objects.values_list('category__name', flat=True).distinct()
    context = {
        "events": events,
        "categories": categories,
        "user": request.user,
        "is_participant": request.user.groups.filter(name='Participant').exists() if request.user.is_authenticated else False,
        "is_organizer": request.user.groups.filter(name='Organizer').exists() if request.user.is_authenticated else False,
        "is_admin": request.user.groups.filter(name='Admin').exists() if request.user.is_authenticated else False,
    }
    return render(request, "events.html", context)

def event_detail(request, id):
    event = get_object_or_404(
        Event.objects
        .prefetch_related('participant')
        .select_related('category')
        .annotate(participant_num=Count("participant")),
        id=id
    )
    context = {
        'event': event,
        'user': request.user,
        'is_participant': request.user.groups.filter(name='Participant').exists() if request.user.is_authenticated else False,
        'is_organizer': request.user.groups.filter(name='Organizer').exists() if request.user.is_authenticated else False,
        'is_admin': request.user.groups.filter(name='Admin').exists() if request.user.is_authenticated else False,
    }
    return render(request, 'event_detail.html', context)

@login_required
@user_passes_test(is_organizer, login_url='no-permission')
def update_event(request, id):
    event = get_object_or_404(Event, id=id)
    if request.user != event.organizer:
        return redirect('no-permission')
    
    event_form = EventForm(instance=event)
    if request.method == 'POST':
        event_form = EventForm(request.POST, instance=event)
        if event_form.is_valid():
            event_form.save()
            messages.success(request, "Event Updated Successfully")
            return redirect('event_detail', id)
    context = {
        "event_form": event_form,
        "is_organizer": request.user.groups.filter(name='Organizer').exists() if request.user.is_authenticated else False,
    }
    return render(request, "create_event.html", context)

@login_required
@user_passes_test(is_organizer, login_url='no-permission')
def delete_event(request, id):
    event = get_object_or_404(Event, id=id)
    if request.user != event.organizer:
        return redirect('no-permission')
    
    if request.method == 'POST':
        event.delete()
        messages.success(request, "Event Deleted Successfully")
        return redirect('view_events')
    return render(request, "event_detail.html")

@login_required
@user_passes_test(is_participant, login_url='no-permission')
def rsvp_event(request, id):
    event = get_object_or_404(Event, id=id)
    if request.method == 'POST':
        if request.user not in event.participant.all():
            event.participant.add(request.user)
            messages.success(request, f"You have successfully RSVP'd to {event.name}!")
            
            # Send confirmation email
            subject = f"RSVP Confirmation for {event.name}"
            message = f"""
            Hello {request.user.first_name},

            Thank you for RSVPing to {event.name}!
            Event Details:
            - Date: {event.date}
            - Location: {event.location}
            - Category: {event.category.name}

            We look forward to seeing you there!

            Best regards,
            The EventHub Team
            """
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                fail_silently=False,
            )
        else:
            messages.info(request, f"You have already RSVP'd to {event.name}.")
        return redirect('event_detail', id=id)
    return redirect('event_detail', id=id)

@login_required
@user_passes_test(is_participant, login_url='no-permission')
def participant_dashboard(request):
    user = request.user
    rsvped_events = (
        Event.objects
        .filter(rsvp_events=user)
        .select_related('category')
        .annotate(participant_num=Count("participant"))
        .order_by('date')
    )
    context = {
        "rsvped_events": rsvped_events,
        "user": user,
        "is_participant": request.user.groups.filter(name='Participant').exists() if request.user.is_authenticated else False,
        "is_organizer": request.user.groups.filter(name='Organizer').exists() if request.user.is_authenticated else False,
        "is_admin": request.user.groups.filter(name='Admin').exists() if request.user.is_authenticated else False,
    }
    return render(request, "participant_dashboard.html", context)

@login_required
@user_passes_test(is_organizer, login_url='no-permission')
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully.")
            return redirect('dashboard')
    else:
        form = CategoryForm()
    context = {
        "form": form,
        "action": "Create",
    }
    return render(request, "category_form.html", context)

@login_required
@user_passes_test(is_organizer, login_url='no-permission')
def edit_category(request, id):
    category = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully.")
            return redirect('dashboard')
    else:
        form = CategoryForm(instance=category)
    context = {
        "form": form,
        "action": "Update",
    }
    return render(request, "category_form.html", context)

@login_required
@user_passes_test(is_organizer, login_url='no-permission')
def delete_category(request, id):
    category = get_object_or_404(Category, id=id)
    if Event.objects.filter(category=category).exists():
        messages.error(request, "Cannot delete category because it is associated with events.")
        return redirect('dashboard')
    if request.method == 'POST':
        category.delete()
        messages.success(request, "Category deleted successfully.")
        return redirect('dashboard')
    return redirect('dashboard')