from django.urls import path
from events.views import home, create_event, dashboard, view_events, event_detail, update_event, delete_event, rsvp_event, participant_dashboard

urlpatterns = [
    path('', home, name='home'),
    path('create/', create_event, name='create_event'),
    path('dashboard/', dashboard, name='dashboard'),
    path('events/', view_events, name='view_events'),
    path('event/<int:id>/', event_detail, name='event_detail'),
    path('event/<int:id>/update/', update_event, name='update_event'),
    path('event/<int:id>/delete/', delete_event, name='delete_event'),
    path('event/<int:id>/rsvp/', rsvp_event, name='rsvp_event'),
    path('participant/dashboard/', participant_dashboard, name='participant_dashboard'),
]