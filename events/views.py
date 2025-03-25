from django.shortcuts import render, redirect
from django.contrib import messages
from events.forms import EventForm, CategoryForm
from events.models import Event, Category
from django.db.models import Q, Count
from django.utils.dateparse import parse_date
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test, login_required, permission_required
from django.core.mail import send_mail
from django.views.generic import View, ListView,CreateView,DetailView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin,UserPassesTestMixin
from django.conf import settings
from django.urls import reverse_lazy

def is_organizer(user):
    return user.groups.filter(name='Organizer').exists()

def is_participant(user):
    return user.groups.filter(name='Participant').exists()

def is_admin(user):
    return user.groups.filter(name='Admin').exists()

@login_required
def dashboard(request):
    if is_organizer(request.user):
        return redirect('organizer_dashboard')
    elif is_participant(request.user):
        return redirect('participant_dashboard')
    elif is_admin(request.user):
        return redirect('admin-dashboard')
    return redirect('no-permission')

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

class HomeView(ListView):
    model=Event
    context_object_name="upcoming_events"
    template_name="homepage.html"
    
    def get_queryset(self):
        queryset=(
            Event.objects.prefetch_related('participant')
            .select_related('category')
            .filter(date__gte=timezone.now())
            .order_by('date')
            .annotate(participant_num=Count("participant"))
        ).order_by('?')[:6]
        return queryset
    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['user']=self.request.user
        context['is_participant']=self.request.user.groups.filter(name='Participant').exists() if self.request.user.is_authenticated else False
        context['is_organizer']=self.request.user.groups.filter(name='Organizer').exists() if self.request.user.is_authenticated else False
        context['is_admin']=self.request.user.groups.filter(name='Admin').exists() if self.request.user.is_authenticated else False
    
    
@login_required
@permission_required("events.add_event", login_url='no-permission')
def create_event(request):
    event_form = EventForm()
    if request.method == 'POST':
        event_form = EventForm(request.POST, request.FILES)
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

class CreateEventView(LoginRequiredMixin,PermissionRequiredMixin,CreateView):
    model=Event
    form_class=EventForm
    template_name="create_event.html"
    success_url=reverse_lazy('create_event')
    login_url='sign-in'
    permission_required='events.add_event'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method == 'POST':
            kwargs['files'] = self.request.FILES
        return kwargs

    def form_valid(self, form):
        try:
            event = form.save(commit=False)
            event.organizer = self.request.user
            event.save()
            form.save_m2m()
            messages.success(self.request, "Event created Successfully")
            return super().form_valid(form)
        
        except Exception as e:
            messages.error(self.request, f"Error creating event: {str(e)}")
            return self.form_invalid(form)
            
    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors in the form.")
        return super().form_invalid(form)
    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['is_organizer']=self.request.user.groups.filter(name='Organizer').exists() if self.request.user.is_authenticated else False
        context['event_form']=context['form']
    
@login_required
@user_passes_test(is_organizer, login_url='no-permission')
def organizer_dashboard(request):
    type = request.GET.get('type', 'all')
    base_query = Event.objects.filter(organizer=request.user).select_related('category').prefetch_related('participant')
    counts = base_query.aggregate(
        total_participants=Count('participant', distinct=True),
        total_events=Count('id', distinct=True),
        upcoming_events=Count('id', filter=Q(date__gt=timezone.now()), distinct=True),
        past_events=Count('id', filter=Q(date__lt=timezone.now()), distinct=True)
    )
    if type == 'upcoming':
        events = base_query.filter(date__gt=timezone.now())
    elif type == 'past':
        events = base_query.filter(date__lt=timezone.now())
    else:
        events = base_query
    events = events.annotate(participant_count=Count('participant')).order_by('date')
    categories = Category.objects.annotate(event_count=Count('event', filter=Q(event__organizer=request.user)))
    context = {
        "counts": counts,
        "events": events,
        "categories": categories,
        "user": request.user,
        "current_type": type,
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

class EventsListView(ListView):
    template_name='events.html'
    model=Event
    context_object_name='events'
    
    def get_queryset(self):
        type = self.request.GET.get('type', 'All')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        events = (
            Event.objects.prefetch_related('participant')
            .select_related('category')
            .annotate(participant_num=Count("participant"))
        )
        search = self.request.GET.get('search', '')
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
        return events
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] =Event.objects.values_list('category__name', flat=True).distinct()
        context['user']=self.request.user
        context['is_participant']= self.request.user.groups.filter(name='Participant').exists() if self.request.user.is_authenticated else False
        context['is_organizer']= self.request.user.groups.filter(name='Organizer').exists() if self.request.user.is_authenticated else False
        context['is_admin']= self.request.user.groups.filter(name='Admin').exists() if self.request.user.is_authenticated else False
        return context
    
    
def event_detail(request, id):
    try:
        event = (
            Event.objects
            .prefetch_related('participant')
            .select_related('category')
            .annotate(participant_num=Count("participant"))
            .get(id=id)
        )
    except Event.DoesNotExist:
        messages.error(request, "Event not found")
        return redirect('view_events')
    
    context = {
        'event': event,
        'user': request.user,
        'is_participant': request.user.groups.filter(name='Participant').exists() if request.user.is_authenticated else False,
        'is_organizer': request.user.groups.filter(name='Organizer').exists() if request.user.is_authenticated else False,
        'is_admin': request.user.groups.filter(name='Admin').exists() if request.user.is_authenticated else False,
    }
    return render(request, 'event_detail.html', context)


class EventDetailView(DetailView):
    model = Event
    template_name = 'event_detail.html'
    context_object_name = 'event'
    pk_url_kwarg = 'id'

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Event.DoesNotExist:
            messages.error(request, "Event not found")
            return redirect('view_events')

    def get_queryset(self):
        queryset= (
            super().get_queryset()
            .prefetch_related('participant')
            .select_related('category')
            .annotate(participant_num=Count("participant"))
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['is_participant'] = self.request.user.groups.filter(name='Participant').exists() if self.request.user.is_authenticated else False
        context['is_organizer'] = self.request.user.groups.filter(name='Organizer').exists() if self.request.user.is_authenticated else False
        context['is_admin'] = self.request.user.groups.filter(name='Admin').exists() if self.request.user.is_authenticated else False
        return context


@login_required
@permission_required("events.change_event", login_url='no-permission')
def update_event(request, id):
    try:
        event = Event.objects.get(id=id)
    except Event.DoesNotExist:
        messages.error(request, "Event not found")
        return redirect('organizer_dashboard')
        
    if request.user != event.organizer:
        return redirect('no-permission')
    
    event_form = EventForm(instance=event)
    if request.method == 'POST':
        event_form = EventForm(request.POST, instance=event)
        if event_form.is_valid():
            event_form.save()
            messages.success(request, "Event Updated Successfully")
            return redirect('event_detail', id=id)
    context = {
        "event_form": event_form,
        "is_organizer": request.user.groups.filter(name='Organizer').exists() if request.user.is_authenticated else False,
    }
    return render(request, "create_event.html", context)

@login_required
@permission_required("events.delete_event", login_url='no-permission')
def delete_event(request, id):
    try:
        event = Event.objects.get(id=id)
    except Event.DoesNotExist:
        messages.error(request, "Event not found")
        return redirect('organizer_dashboard')
        
    if request.user != event.organizer:
        return redirect('no-permission')
    
    if request.method == 'POST':
        event.delete()
        messages.success(request, "Event Deleted Successfully")
        return redirect('view_events')
    return render(request, "event_detail.html")

class EventDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Event
    template_name = "event_detail.html"
    permission_required = "events.delete_event"
    login_url = 'no-permission'
    success_url = reverse_lazy('view_events')
    pk_url_kwarg = 'id'
    
    def get_object(self, queryset=None):
        try:
            obj = Event.objects.get(id=self.kwargs['id'])
            if self.request.user != obj.organizer:
                return redirect('no-permission')
            return obj
        except Event.DoesNotExist:
            messages.error(self.request, "Event not found")
            return redirect('organizer_dashboard')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not isinstance(self.object, Event):
            return self.object
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(request, "Event Deleted Successfully")
        return redirect(success_url)
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not isinstance(obj, Event):
            return obj
        return super().dispatch(request, *args, **kwargs)

@login_required
@user_passes_test(is_participant, login_url='no-permission')
def rsvp_event(request, id):
    try:
        event = Event.objects.get(id=id)
    except Event.DoesNotExist:
        messages.error(request, "Event not found")
        return redirect('view_events')
        
    if request.method == 'POST':
        if request.user not in event.participant.all():
            event.participant.add(request.user)
            messages.success(request, f"You have successfully RSVP'd to {event.name}!")
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

class RSVPEventView(LoginRequiredMixin,UserPassesTestMixin,View):
    login_url='no-permission'
    
    def test_func(self):
        return is_participant(self.request.user)
    
    def get_event(self,pk):
        try:
            return Event.objects.get(id=pk)
        except Event.DoesNotExist:
            messages.error(self.request, "Event not found")
            return None
    def get(self,request,*arg,**kwargs):
        return redirect('event_detail', id=self.kwargs['pk'])
    def post(self, request, *args, **kwargs):
        event = self.get_event(self.kwargs['pk'])
        
        if event is None:
            return redirect('event_detail', id=self.kwargs['pk'])
            
        if request.user not in event.participant.all():
            event.participant.add(request.user)
            messages.success(request, f"You have successfully RSVP'd to {event.name}!")
            
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
        
        return redirect('event_detail', id=event.id)

@login_required
@user_passes_test(is_participant, login_url='no-permission')
def participant_dashboard(request):
    user = request.user
    rsvped_events = (
        Event.objects
        .filter(participant=user)
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
@user_passes_test(is_participant, login_url='no-permission')
def cancel_rsvp(request, id):
    try:
        event = Event.objects.get(id=id)
    except Event.DoesNotExist:
        messages.error(request, "Event not found")
        return redirect('participant_dashboard')
        
    if request.method == 'POST':
        if request.user in event.participant.all():
            event.participant.remove(request.user)
            messages.success(request, f"You have successfully canceled your registration for {event.name}.")
        else:
            messages.error(request, "You are not registered for this event.")
        return redirect('participant_dashboard')
    return redirect('participant_dashboard')

@login_required
@permission_required("events.add_category", login_url='no-permission')
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully.")
            return redirect('organizer_dashboard')
    else:
        form = CategoryForm()
    context = {
        "form": form,
        "action": "Create",
    }
    return render(request, "category_form.html", context)

@login_required
@permission_required("events.change_category", login_url='no-permission')
def edit_category(request, id):
    try:
        category = Category.objects.get(id=id)
    except Category.DoesNotExist:
        messages.error(request, "Category not found")
        return redirect('organizer_dashboard')
        
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully.")
            return redirect('organizer_dashboard')
    else:
        form = CategoryForm(instance=category)
    context = {
        "form": form,
        "action": "Update",
    }
    return render(request, "category_form.html", context)

@login_required
@permission_required("events.delete_category", login_url='no-permission')
def delete_category(request, id):
    try:
        category = Category.objects.get(id=id)
    except Category.DoesNotExist:
        messages.error(request, "Category not found")
        return redirect('organizer_dashboard')
        
    if Event.objects.filter(category=category).exists():
        messages.error(request, "Cannot delete category because it is associated with events.")
        return redirect('organizer_dashboard')
    if request.method == 'POST':
        category.delete()
        messages.success(request, "Category deleted successfully.")
        return redirect('organizer_dashboard')
    return redirect('organizer_dashboard')