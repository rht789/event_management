from django.urls import path
from events.views import home, create_event, organizer_dashboard, view_events, event_detail, update_event, delete_event, rsvp_event, participant_dashboard,create_category,edit_category,delete_category,dashboard,cancel_rsvp

urlpatterns = [
    path('', home, name='home'),
    path('create/', create_event, name='create_event'),
    path('dashboard/', dashboard, name='dashboard'),
    path('organizer/dashboard/', organizer_dashboard, name='organizer_dashboard'),
    path('events/', view_events, name='view_events'),
    path('event/<int:id>/', event_detail, name='event_detail'),
    path('event/<int:id>/update/', update_event, name='update_event'),
    path('event/<int:id>/delete/', delete_event, name='delete_event'),
    path('event/<int:id>/rsvp/', rsvp_event, name='rsvp_event'),
    path('event/<int:id>/cancel/', cancel_rsvp, name='cancel_rsvp'),
    path('participant/dashboard/', participant_dashboard, name='participant_dashboard'),
    path('category/create/', create_category, name='create_category'),
    path('category/<int:id>/edit/', edit_category, name='edit_category'),
    path('category/<int:id>/delete/', delete_category, name='delete_category'),
]