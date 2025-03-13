from django.urls import path
from events.views import *

urlpatterns = [
    path('create_event/', create_event, name='create_event'),
    path('dashboard/', dashboard, name='dashboard'),
    path('events/', view_events, name='events'),
    path('events/<int:id>', event_detail, name='event_detail'),
    path('update_event/<int:id>', update_event, name='update_event'),
    path('delete_event/<int:id>', delete_event, name='delete_event'),
    path('event/<int:id>/book/', book_event, name='book_event'),
]
