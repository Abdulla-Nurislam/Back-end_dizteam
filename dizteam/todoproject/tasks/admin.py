from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'category', 'created_date', 'is_completed')
    list_filter = ('is_completed', 'category')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_date'
