from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()
    color = models.CharField(max_length=7, default='#000000')
    
    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    assets = models.ImageField(upload_to='events_asset', blank=True, null=True, default="events_asset/default.jpg")
    participant = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='rsvp_events', blank=True)
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='events_organized'
    )
    
    def __str__(self):
        return self.name