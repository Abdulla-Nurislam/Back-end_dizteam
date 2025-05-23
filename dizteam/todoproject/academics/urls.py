from django.urls import path
from . import views

urlpatterns = [
    # Class Schedule URLs
    path('schedule/', views.schedule_view, name='schedule'),
    path('schedule/calendar/', views.schedule_calendar_view, name='schedule_calendar'),
    path('schedule/api/events/', views.get_schedule_events, name='get_schedule_events'),
    
    # Grades URLs
    path('grades/', views.grades_view, name='grades'),
    path('grades/course/<int:course_id>/', views.course_grades_detail, name='course_grades_detail'),
    
    # Announcements URLs
    path('announcements/', views.AnnouncementListView.as_view(), name='announcement_list'),
]
