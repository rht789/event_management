from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()
    
    
    def __str__(self):
        return self.name
        
class Participant(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    
    def __str__(self):
        return self.name
        
class Event(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True,null=True)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(blank=True,null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default='1')
    participant = models.ManyToManyField(Participant, related_name='events')
    
    def __str__(self):
        return self.name
    
