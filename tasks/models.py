from django.db import models
from django.contrib.auth.models import User
from categories.models import Category
from django.utils import timezone

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    
    def __str__(self):
        return self.name

class Area(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='areas')
    
    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default='#3498db')  # Default blue color
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tags')
    
    def __str__(self):
        return self.name

class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    
    # New fields inspired by Things3
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    tags = models.ManyToManyField(Tag, blank=True, related_name='tasks')
    deadline = models.DateTimeField(null=True, blank=True)
    today_flag = models.BooleanField(default=False)
    
    # Field to link with events
    event = models.ForeignKey('events.Event', on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    
    class Meta:
        ordering = ['-created_date']
    
    def __str__(self):
        return self.title
    
    @property
    def is_today(self):
        return self.today_flag or (self.deadline and self.deadline.date() == timezone.now().date())
