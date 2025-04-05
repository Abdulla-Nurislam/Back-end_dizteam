from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta

from .models import Event
from .forms import EventForm
from tasks.models import Task

class EventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    
    def get_queryset(self):
        # Get events owned by user and shared with user
        user_events = Event.objects.filter(
            Q(owner=self.request.user) | Q(shared_with=self.request.user)
        ).distinct()
        
        # Apply date filter if provided
        date_filter = self.request.GET.get('date')
        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                user_events = user_events.filter(
                    Q(start_time__date=filter_date) | Q(end_time__date=filter_date)
                )
            except ValueError:
                pass
        
        return user_events
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date_filter'] = self.request.GET.get('date', '')
        return context

class EventDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    
    def test_func(self):
        event = self.get_object()
        # Allow access if user is owner or event is shared with user
        return (event.owner == self.request.user or 
                self.request.user in event.shared_with.all())
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()
        
        # Get related tasks
        context['related_tasks'] = Task.objects.filter(event=event)
        
        return context

class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('event_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Event successfully created!')
        return super().form_valid(form)

class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    
    def test_func(self):
        event = self.get_object()
        return event.owner == self.request.user
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_success_url(self):
        return reverse_lazy('event_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Event successfully updated!')
        return super().form_valid(form)

class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Event
    template_name = 'events/event_confirm_delete.html'
    success_url = reverse_lazy('event_list')
    
    def test_func(self):
        event = self.get_object()
        return event.owner == self.request.user
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Event successfully deleted!')
        return super().delete(request, *args, **kwargs)

@login_required
def calendar_view(request):
    """View for displaying the calendar with events and tasks"""
    return render(request, 'events/calendar.html')

@login_required
def get_calendar_events(request):
    """API endpoint to get events for calendar in JSON format"""
    start = request.GET.get('start')
    end = request.GET.get('end')
    
    if not start or not end:
        return JsonResponse({'error': 'Start and end parameters are required'}, status=400)
    
    try:
        start_date = datetime.fromisoformat(start.replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(end.replace('Z', '+00:00'))
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    
    # Get events in date range
    events = Event.objects.filter(
        Q(owner=request.user) | Q(shared_with=request.user),
        Q(start_time__lte=end_date) & Q(end_time__gte=start_date)
    ).distinct()
    
    # Get tasks with deadlines in date range
    tasks = Task.objects.filter(
        owner=request.user,
        deadline__isnull=False,
        deadline__gte=start_date,
        deadline__lte=end_date
    )
    
    # Format events for FullCalendar
    calendar_events = []
    
    for event in events:
        calendar_events.append({
            'id': f'event_{event.pk}',
            'title': event.title,
            'start': event.start_time.isoformat(),
            'end': event.end_time.isoformat(),
            'url': reverse_lazy('event_detail', kwargs={'pk': event.pk}),
            'allDay': event.all_day,
            'extendedProps': {
                'location': event.location,
                'description': event.description,
                'type': 'event'
            },
            'backgroundColor': '#3788d8',  # Blue for events
            'borderColor': '#3788d8',
        })
    
    for task in tasks:
        calendar_events.append({
            'id': f'task_{task.pk}',
            'title': f'Task: {task.title}',
            'start': task.deadline.isoformat(),
            'url': reverse_lazy('task_detail', kwargs={'pk': task.pk}),
            'allDay': False,
            'extendedProps': {
                'description': task.description,
                'type': 'task'
            },
            'backgroundColor': '#28a745',  # Green for tasks
            'borderColor': '#28a745',
        })
    
    return JsonResponse(calendar_events, safe=False)
