from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db.models import Avg, Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Course, ClassSchedule, Grade, Announcement

# Class Schedule Views
@login_required
def schedule_view(request):
    """View for displaying the student's class schedule"""
    # Get the current day of the week
    today = timezone.now().strftime('%a').upper()[:3]
    
    # Get all courses the student is enrolled in
    courses = Course.objects.filter(students=request.user)
    
    # Get schedule for these courses
    schedule = ClassSchedule.objects.filter(course__in=courses, is_active=True).order_by('day_of_week', 'start_time')
    
    # Filter by day if requested
    day_filter = request.GET.get('day')
    if day_filter:
        schedule = schedule.filter(day_of_week=day_filter)
    
    context = {
        'schedule': schedule,
        'today': today,
        'day_filter': day_filter,
        'days': ClassSchedule.DAY_CHOICES,
    }
    
    return render(request, 'academics/schedule.html', context)

@login_required
def schedule_calendar_view(request):
    """Calendar view for class schedule"""
    return render(request, 'academics/schedule_calendar.html')

@login_required
def get_schedule_events(request):
    """API endpoint to get class schedule for calendar in JSON format"""
    start = request.GET.get('start')
    end = request.GET.get('end')
    
    if not start or not end:
        return JsonResponse({'error': 'Start and end parameters are required'}, status=400)
    
    try:
        start_date = datetime.fromisoformat(start.replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(end.replace('Z', '+00:00'))
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    
    # Get all courses the student is enrolled in
    courses = Course.objects.filter(students=request.user)
    
    # Get schedule for these courses
    schedule_items = ClassSchedule.objects.filter(course__in=courses, is_active=True)
    
    # Format events for FullCalendar
    calendar_events = []
    
    # Calculate the date range
    delta = end_date.date() - start_date.date()
    
    # For each day in the range
    for i in range(delta.days + 1):
        current_date = start_date.date() + timedelta(days=i)
        day_of_week = current_date.strftime('%a').upper()[:3]
        
        # Get classes for this day of the week
        day_classes = schedule_items.filter(day_of_week=day_of_week)
        
        # Add each class as an event
        for class_item in day_classes:
            # Create datetime objects for this specific date
            start_datetime = datetime.combine(current_date, class_item.start_time)
            end_datetime = datetime.combine(current_date, class_item.end_time)
            
            calendar_events.append({
                'id': f'class_{class_item.id}_{current_date}',
                'title': class_item.course.name,
                'start': start_datetime.isoformat(),
                'end': end_datetime.isoformat(),
                'extendedProps': {
                    'location': class_item.location,
                    'course_code': class_item.course.code,
                    'type': 'class'
                },
                'backgroundColor': '#3788d8',  # Blue for classes
                'borderColor': '#3788d8',
            })
    
    return JsonResponse(calendar_events, safe=False)

# Grades Views
@login_required
def grades_view(request):
    """View for displaying the student's grades"""
    # Get all courses the student is enrolled in
    courses = Course.objects.filter(students=request.user)
    
    # Filter by course if requested
    course_filter = request.GET.get('course')
    if course_filter:
        selected_course = get_object_or_404(Course, id=course_filter, students=request.user)
        grades = Grade.objects.filter(student=request.user, course=selected_course)
    else:
        selected_course = None
        grades = Grade.objects.filter(student=request.user, course__in=courses)
    
    # Calculate course averages
    course_averages = []
    for course in courses:
        course_grades = Grade.objects.filter(student=request.user, course=course)
        if course_grades.exists():
            # Calculate weighted average
            total_weighted_score = 0
            total_weight = 0
            
            for grade in course_grades:
                weighted_score = (grade.points_earned / grade.points_possible) * grade.weight
                total_weighted_score += weighted_score
                total_weight += grade.weight
            
            if total_weight > 0:
                average = (total_weighted_score / total_weight) * 100
            else:
                average = 0
                
            course_averages.append({
                'course': course,
                'average': average,
                'letter_grade': get_letter_grade(average),
                'grades_count': course_grades.count(),
            })
    
    context = {
        'grades': grades,
        'courses': courses,
        'selected_course': selected_course,
        'course_averages': course_averages,
    }
    
    return render(request, 'academics/grades.html', context)

@login_required
def course_grades_detail(request, course_id):
    """Detailed view of grades for a specific course"""
    course = get_object_or_404(Course, id=course_id, students=request.user)
    grades = Grade.objects.filter(student=request.user, course=course)
    
    # Calculate weighted average
    total_weighted_score = 0
    total_weight = 0
    
    for grade in grades:
        weighted_score = (grade.points_earned / grade.points_possible) * grade.weight
        total_weighted_score += weighted_score
        total_weight += grade.weight
    
    if total_weight > 0:
        average = (total_weighted_score / total_weight) * 100
    else:
        average = 0
    
    # Group grades by type
    grade_types = {}
    for grade in grades:
        if grade.grade_type not in grade_types:
            grade_types[grade.grade_type] = []
        grade_types[grade.grade_type].append(grade)
    
    context = {
        'course': course,
        'grades': grades,
        'average': average,
        'letter_grade': get_letter_grade(average),
        'grade_types': grade_types,
    }
    
    return render(request, 'academics/course_grades_detail.html', context)

# Announcements Views
class AnnouncementListView(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = 'academics/announcement_list.html'
    context_object_name = 'announcements'
    
    def get_queryset(self):
        # Get global announcements and those targeted to this student
        return Announcement.objects.filter(
            Q(is_global=True) | Q(target_students=self.request.user)
        ).order_by('-date_posted')

# Helper functions
def get_letter_grade(percentage):
    """Convert percentage to letter grade"""
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
