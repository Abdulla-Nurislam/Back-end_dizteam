from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class Event(models.Model):
    REPEAT_CHOICES = [
        ('none', 'No repeat'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True, null=True)
    all_day = models.BooleanField(default=False)
    
    # Repeat options
    repeat = models.CharField(max_length=20, choices=REPEAT_CHOICES, default='none')
    repeat_until = models.DateField(null=True, blank=True)
    
    # Sharing and ownership
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    shared_with = models.ManyToManyField(User, related_name='shared_events', blank=True)
    
    # Unique ID for external calendar sync (future feature)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # Notification settings
    notify_before = models.IntegerField(default=30, help_text="Minutes before event to send notification")
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_time']
    
    def __str__(self):
        return self.title
    
    @property
    def is_past(self):
        return self.end_time < timezone.now()
    
    @property
    def is_ongoing(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time
