from django.urls import path
from events.views import  organizer_dashboard, update_event, rsvp_event, participant_dashboard,create_category,edit_category,delete_category,dashboard,cancel_rsvp,HomeView,CreateEventView,EventsListView,EventDetailView,EventDeleteView, RSVPEventView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('create/', CreateEventView.as_view(), name='create_event'),
    path('dashboard/', dashboard, name='dashboard'),
    path('organizer/dashboard/', organizer_dashboard, name='organizer_dashboard'),
    path('events/', EventsListView.as_view(), name='view_events'),
    path('event/<int:id>/', EventDetailView.as_view(), name='event_detail'),
    path('event/<int:id>/update/', update_event, name='update_event'),
    path('event/<int:id>/delete/', EventDeleteView.as_view(), name='delete_event'),
    path('event/<int:id>/rsvp/', RSVPEventView.as_view(), name='rsvp_event'),
    path('event/<int:id>/cancel/', cancel_rsvp, name='cancel_rsvp'),
    path('participant/dashboard/', participant_dashboard, name='participant_dashboard'),
    path('category/create/', create_category, name='create_category'),
    path('category/<int:id>/edit/', edit_category, name='edit_category'),
    path('category/<int:id>/delete/', delete_category, name='delete_category'),
]