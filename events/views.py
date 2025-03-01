from django.shortcuts import render,redirect
from django.contrib import messages
from events.forms import EventForm
from events.models import Event, Category, Participant
from django.db.models import Q,Count
from django.utils.dateparse import parse_date
from django.utils import timezone

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
    }
    return render(request, "home.html", context)

def create_event(request):
    event_form = EventForm()
    if request.method == 'POST':
        event_form=EventForm(request.POST)
        if event_form.is_valid():
            event_form.save()
            messages.success(request,"Event created Sucessfully")
            return redirect('create_event')
    context = {"event_form": event_form}
    return render(request, "create_event.html", context)

def dashboard(request):
    type = request.GET.get('type','all')
    base_query = Event.objects.select_related('category').prefetch_related('participant')
    
    counts = base_query.aggregate(
        total_participants = Count('participant', distinct=True),
        total_events = Count('id', distinct=True),
        upcoming_events = Count('id', filter=Q(date__gt=timezone.now()),distinct=True),
        past_events = Count('id', filter=Q(date__lt=timezone.now()),distinct=True)
    )
    if type == 'upcoming':
        events = base_query.filter(date__gt=timezone.now())
    elif type == 'past':
        events = base_query.filter(date__lt=timezone.now())
    else:
        events = base_query
    categories = (
        events
        .values('category__name')
        .annotate(event_count=Count('id', distinct=True))
        .order_by('category__name')
    )
    event_today = base_query.filter(date=timezone.now())
    context = {
        "counts" : counts,
        "categories" : categories,
        "event_today" : event_today
    }
    return render(request,"dashboard.html", context=context)

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
        "categories": categories
    }
    return render(request, "events.html", context)

def event_detail(request, id):
    event = (
        Event.objects
        .prefetch_related('participant')
        .select_related('category')
        .annotate(participant_num=Count("participant"))
        .get(id=id)
    )

    context = {
        'event': event
    }
    return render(request, 'event_detail.html', context)

def update_event(request,id):
    event = Event.objects.get(id=id)
    event_form = EventForm(instance=event)
    if request.method == 'POST':
        event_form=EventForm(request.POST,instance=event)
        if event_form.is_valid():
            event_form.save()
            messages.success(request,"Event Updated Sucessfully")
            return redirect('event_detail',id)
    context = {"event_form": event_form}
    return render(request, "create_event.html", context)

def delete_event(request,id):
    if request.method == 'POST':    
        event = Event.objects.get(id=id)
        event.delete()
        messages.success(request,"Event Deleted Sucessfully, showing next event detail")
        return redirect('event_detail',id+1)
    return render(request, "event_detail.html")
