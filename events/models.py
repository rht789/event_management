from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()
    
    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    participant = models.ManyToManyField(User, related_name='rsvp_events', blank=True)
    organizer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='events_organized',
        default=1
    )
    
    def __str__(self):
        return self.name