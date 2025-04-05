from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time', 'owner', 'all_day', 'repeat')
    list_filter = ('all_day', 'repeat', 'owner')
    search_fields = ('title', 'description', 'location')
    date_hierarchy = 'start_time'
    filter_horizontal = ('shared_with',)
