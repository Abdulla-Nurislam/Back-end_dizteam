from django.contrib import admin
from .models import Course, ClassSchedule, Grade, Announcement

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'credits')
    search_fields = ('code', 'name')
    filter_horizontal = ('students',)

@admin.register(ClassSchedule)
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ('course', 'day_of_week', 'start_time', 'end_time', 'location', 'is_active')
    list_filter = ('day_of_week', 'is_active')
    search_fields = ('course__code', 'course__name', 'location')

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'title', 'grade_type', 'points_earned', 'points_possible', 'date_added')
    list_filter = ('grade_type', 'course')
    search_fields = ('student__username', 'course__code', 'title')

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'date_posted')
    list_filter = ('date_posted', 'course')
    search_fields = ('title', 'content')
    date_hierarchy = 'date_posted'
