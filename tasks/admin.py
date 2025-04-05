from django.contrib import admin
from .models import Task, Project, Area, Tag

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'is_completed', 'deadline', 'today_flag', 'project', 'area')
    list_filter = ('is_completed', 'today_flag', 'owner', 'project', 'area')
    search_fields = ('title', 'description')
    date_hierarchy = 'deadline'
    filter_horizontal = ('tags',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_date')
    list_filter = ('owner',)
    search_fields = ('name', 'description')

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner')
    list_filter = ('owner',)
    search_fields = ('name', 'description')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'owner')
    list_filter = ('owner',)
    search_fields = ('name',)
