from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Course(models.Model):
    """Model representing a university course"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    credits = models.IntegerField(default=3)
    
    # Relationships
    students = models.ManyToManyField(User, related_name='courses')
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class ClassSchedule(models.Model):
    """Model representing a scheduled class session"""
    DAY_CHOICES = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='schedule')
    day_of_week = models.CharField(max_length=3, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=100)
    
    # For recurring schedules with exceptions
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.course.code} - {self.get_day_of_week_display()} {self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}"

class Grade(models.Model):
    """Model representing a grade for an assignment or exam"""
    GRADE_TYPES = [
        ('EXAM', 'Exam'),
        ('QUIZ', 'Quiz'),
        ('ASSIGNMENT', 'Assignment'),
        ('PROJECT', 'Project'),
        ('MIDTERM', 'Midterm'),
        ('FINAL', 'Final'),
        ('OTHER', 'Other'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='grades')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    grade_type = models.CharField(max_length=20, choices=GRADE_TYPES)
    
    # Grade can be stored as points or percentage
    points_earned = models.DecimalField(max_digits=5, decimal_places=2)
    points_possible = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Metadata
    date_added = models.DateField(default=timezone.now)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=1.0, 
                                help_text="Weight of this grade in the course total")
    
    @property
    def percentage(self):
        """Calculate percentage score"""
        if self.points_possible == 0:
            return 0
        return (self.points_earned / self.points_possible) * 100
    
    @property
    def letter_grade(self):
        """Convert percentage to letter grade"""
        percentage = self.percentage
        if percentage >= 95:
            return 'A+'
        elif percentage >= 90:
            return 'A'
        elif percentage >= 85:
            return 'A-'
        elif percentage >= 80:
            return 'B+'
        elif percentage >= 75:
            return 'B'
        elif percentage >= 70:
            return 'B-'
        elif percentage >= 65:
            return 'C+'
        elif percentage >= 60:
            return 'C'
        elif percentage >= 55:
            return 'C-'
        elif percentage >= 50:
            return 'D'
        else:
            return 'F'
    
    def __str__(self):
        return f"{self.course.code} - {self.title} - {self.letter_grade}"

class Announcement(models.Model):
    """Model representing university announcements"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    
    # Optional course association
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, 
                              related_name='announcements', null=True, blank=True)
    
    # For targeting specific students or all students
    is_global = models.BooleanField(default=True)
    target_students = models.ManyToManyField(User, related_name='targeted_announcements', blank=True)
    
    def __str__(self):
        return self.title
