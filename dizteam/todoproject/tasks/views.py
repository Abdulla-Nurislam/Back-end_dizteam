from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta, date
from calendar import monthrange
import calendar
from django.http import HttpResponse

def debug_view(request):
    """Simple view for debugging URLs"""
    return HttpResponse("Debug view is working! Tasks app is properly connected.")

from .models import Task, Project, Area, Tag
from categories.models import Category
from .forms import TaskForm, ProjectForm, AreaForm, TagForm

# Task Views
class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        queryset = Task.objects.filter(owner=self.request.user)
        
        # Category filter
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Project filter
        project_id = self.request.GET.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # Area filter
        area_id = self.request.GET.get('area')
        if area_id:
            queryset = queryset.filter(area_id=area_id)
        
        # Tag filter
        tag_id = self.request.GET.get('tag')
        if tag_id:
            queryset = queryset.filter(tags__id=tag_id)
            
        # Status filter
        status = self.request.GET.get('status')
        if status == 'completed':
            queryset = queryset.filter(is_completed=True)
        elif status == 'active':
            queryset = queryset.filter(is_completed=False)
        
        # Search
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['projects'] = Project.objects.filter(owner=self.request.user)
        context['areas'] = Area.objects.filter(owner=self.request.user)
        context['tags'] = Tag.objects.filter(owner=self.request.user)
        
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_project'] = self.request.GET.get('project', '')
        context['selected_area'] = self.request.GET.get('area', '')
        context['selected_tag'] = self.request.GET.get('tag', '')
        context['status'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('search', '')
        
        return context

class TodayTaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/today_task_list.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        today = timezone.now().date()
        
        # Get tasks marked with today_flag or with deadline today
        queryset = Task.objects.filter(
            owner=self.request.user,
            is_completed=False
        ).filter(
            Q(today_flag=True) | 
            Q(deadline__date=today)
        )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today_date'] = timezone.now().date()
        return context

class TaskDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    
    def test_func(self):
        task = self.get_object()
        return task.owner == self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.get_object()
        
        if task.event:
            context['event'] = task.event
            
        return context

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['projects'] = Project.objects.filter(owner=self.request.user)
        context['areas'] = Area.objects.filter(owner=self.request.user)
        context['tags'] = Tag.objects.filter(owner=self.request.user)
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Task successfully created!')
        return super().form_valid(form)

class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    
    def test_func(self):
        task = self.get_object()
        return task.owner == self.request.user
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['projects'] = Project.objects.filter(owner=self.request.user)
        context['areas'] = Area.objects.filter(owner=self.request.user)
        context['tags'] = Tag.objects.filter(owner=self.request.user)
        return context
    
    def get_success_url(self):
        return reverse_lazy('task_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Task successfully updated!')
        return super().form_valid(form)

class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('task_list')
    
    def test_func(self):
        task = self.get_object()
        return task.owner == self.request.user
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Task successfully deleted!')
        return super().delete(request, *args, **kwargs)

@login_required
def task_toggle_completion(request, pk):
    task = get_object_or_404(Task, pk=pk, owner=request.user)
    task.is_completed = not task.is_completed
    task.save()
    
    status_message = "completed" if task.is_completed else "returned to active"
    messages.success(request, f'Task "{task.title}" {status_message}!')
    
    # Return to the page from which the request was made
    next_url = request.GET.get('next', reverse_lazy('task_list'))
    return redirect(next_url)

@login_required
def task_toggle_today(request, pk):
    task = get_object_or_404(Task, pk=pk, owner=request.user)
    task.today_flag = not task.today_flag
    task.save()
    
    status_message = "added to today" if task.today_flag else "removed from today"
    messages.success(request, f'Task "{task.title}" {status_message}!')
    
    # Return to the page from which the request was made
    next_url = request.GET.get('next', reverse_lazy('task_list'))
    return redirect(next_url)

# Project Views
class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'tasks/project_list.html'
    context_object_name = 'projects'
    
    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

class ProjectDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Project
    template_name = 'tasks/project_detail.html'
    
    def test_func(self):
        project = self.get_object()
        return project.owner == self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        
        # Get tasks for this project
        context['tasks'] = Task.objects.filter(
            owner=self.request.user,
            project=project
        )
        
        return context

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'tasks/project_form.html'
    success_url = reverse_lazy('project_list')
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Project successfully created!')
        return super().form_valid(form)

class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'tasks/project_form.html'
    
    def test_func(self):
        project = self.get_object()
        return project.owner == self.request.user
    
    def get_success_url(self):
        return reverse_lazy('project_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Project successfully updated!')
        return super().form_valid(form)

class ProjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Project
    template_name = 'tasks/project_confirm_delete.html'
    success_url = reverse_lazy('project_list')
    
    def test_func(self):
        project = self.get_object()
        return project.owner == self.request.user
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Project successfully deleted!')
        return super().delete(request, *args, **kwargs)

# Area Views
class AreaListView(LoginRequiredMixin, ListView):
    model = Area
    template_name = 'tasks/area_list.html'
    context_object_name = 'areas'
    
    def get_queryset(self):
        return Area.objects.filter(owner=self.request.user)

class AreaDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Area
    template_name = 'tasks/area_detail.html'
    
    def test_func(self):
        area = self.get_object()
        return area.owner == self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        area = self.get_object()
        
        # Get tasks for this area
        context['tasks'] = Task.objects.filter(
            owner=self.request.user,
            area=area
        )
        
        # Get projects in this area
        context['projects'] = Project.objects.filter(
            owner=self.request.user,
            area=area
        )
        
        return context

class AreaCreateView(LoginRequiredMixin, CreateView):
    model = Area
    form_class = AreaForm
    template_name = 'tasks/area_form.html'
    success_url = reverse_lazy('area_list')
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Area successfully created!')
        return super().form_valid(form)

class AreaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Area
    form_class = AreaForm
    template_name = 'tasks/area_form.html'
    
    def test_func(self):
        area = self.get_object()
        return area.owner == self.request.user
    
    def get_success_url(self):
        return reverse_lazy('area_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Area successfully updated!')
        return super().form_valid(form)

class AreaDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Area
    template_name = 'tasks/area_confirm_delete.html'
    success_url = reverse_lazy('area_list')
    
    def test_func(self):
        area = self.get_object()
        return area.owner == self.request.user
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Area successfully deleted!')
        return super().delete(request, *args, **kwargs)

# Tag Views
class TagListView(LoginRequiredMixin, ListView):
    model = Tag
    template_name = 'tasks/tag_list.html'
    context_object_name = 'tags'
    
    def get_queryset(self):
        return Tag.objects.filter(owner=self.request.user)

class TagDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Tag
    template_name = 'tasks/tag_detail.html'
    
    def test_func(self):
        tag = self.get_object()
        return tag.owner == self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = self.get_object()
        
        # Get tasks with this tag
        context['tasks'] = Task.objects.filter(
            owner=self.request.user,
            tags=tag
        )
        
        return context

class TagCreateView(LoginRequiredMixin, CreateView):
    model = Tag
    form_class = TagForm
    template_name = 'tasks/tag_form.html'
    success_url = reverse_lazy('tag_list')
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Tag successfully created!')
        return super().form_valid(form)

class TagUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Tag
    form_class = TagForm
    template_name = 'tasks/tag_form.html'
    success_url = reverse_lazy('tag_list')
    
    def test_func(self):
        tag = self.get_object()
        return tag.owner == self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Tag successfully updated!')
        return super().form_valid(form)

class TagDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Tag
    template_name = 'tasks/tag_confirm_delete.html'
    success_url = reverse_lazy('tag_list')
    
    def test_func(self):
        tag = self.get_object()
        return tag.owner == self.request.user
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Tag successfully deleted!')
        return super().delete(request, *args, **kwargs)

from django.contrib.auth.decorators import login_required

@login_required
def calendar_view(request):
    """View for displaying the calendar with tasks and events"""
    today = date.today()
    
    # Get query parameters with defaults
    view_type = request.GET.get('view', 'month')  # Default to month view
    
    # Determine which date to show
    if 'date' in request.GET:
        try:
            selected_date = datetime.strptime(request.GET.get('date'), '%Y-%m-%d').date()
        except ValueError:
            selected_date = today
    else:
        selected_date = today
    
    # Get year and month from query params or use current date
    year = int(request.GET.get('year', selected_date.year))
    month = int(request.GET.get('month', selected_date.month))
    
    # Calculate previous and next month/year
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
        
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    
    # Get calendar data for month view
    cal = calendar.monthcalendar(year, month)
    month_days = []
    
    # Get the month name
    current_month_name = calendar.month_name[month]
    
    # For month view, prepare calendar weeks
    if view_type == 'month':
        # Prepare calendar grid with all days in the month
        calendar_weeks = []
        
        # Get first day of the month
        first_day = date(year, month, 1)
        
        # Get last day of the month
        last_day = date(year, month, monthrange(year, month)[1])
        
        # Calculate days from previous month to show
        days_before = first_day.weekday()
        
        # Calculate days from next month to show
        days_after = 6 - last_day.weekday()
        
        # Get days from previous month
        if days_before > 0:
            if month == 1:
                prev_month_days = monthrange(year - 1, 12)[1]
                prev_month_date = 12
                prev_year_date = year - 1
            else:
                prev_month_days = monthrange(year, month - 1)[1]
                prev_month_date = month - 1
                prev_year_date = year
                
            for i in range(days_before):
                day_num = prev_month_days - days_before + i + 1
                month_days.append({
                    'date': date(prev_year_date, prev_month_date, day_num),
                    'tasks': [],
                    'events': [],
                    'has_more': False,
                    'more_count': 0,
                    'month': prev_month_date
                })
        
        # Get days from current month
        for day in range(1, monthrange(year, month)[1] + 1):
            day_date = date(year, month, day)
            
            # Get tasks for this day
            day_tasks = Task.objects.filter(deadline__date=day_date)
            
            # Get events for this day (assuming you have an Event model)
            try:
                from events.models import Event
                day_events = Event.objects.filter(date=day_date)
            except:
                day_events = []
            
            # Check if we need to show "more" indicator
            has_more = len(day_tasks) + len(day_events) > 3
            more_count = len(day_tasks) + len(day_events) - 3 if has_more else 0
            
            month_days.append({
                'date': day_date,
                'tasks': day_tasks[:2] if has_more else day_tasks,
                'events': day_events[:1] if has_more and len(day_tasks) >= 2 else day_events,
                'has_more': has_more,
                'more_count': more_count,
                'month': month
            })
        
        # Get days from next month
        if days_after > 0:
            if month == 12:
                next_month_date = 1
                next_year_date = year + 1
            else:
                next_month_date = month + 1
                next_year_date = year
                
            for i in range(days_after):
                day_num = i + 1
                month_days.append({
                    'date': date(next_year_date, next_month_date, day_num),
                    'tasks': [],
                    'events': [],
                    'has_more': False,
                    'more_count': 0,
                    'month': next_month_date
                })
        
        # Split days into weeks
        for i in range(0, len(month_days), 7):
            calendar_weeks.append(month_days[i:i+7])
    
    # For week view
    if view_type == 'week':
        # Determine the start of the week (Sunday)
        week_start = selected_date - timedelta(days=selected_date.weekday() + 1)
        if week_start.weekday() == 6:  # If it's already Sunday
            week_start = selected_date
        
        # Determine the end of the week (Saturday)
        week_end = week_start + timedelta(days=6)
        
        # Create a list of days in the week
        week_days = []
        for i in range(7):
            day_date = week_start + timedelta(days=i)
            
            # Get tasks for this day
            day_tasks = Task.objects.filter(deadline__date=day_date)
            
            # Get events for this day
            try:
                from events.models import Event
                day_events = Event.objects.filter(date=day_date)
            except:
                day_events = []
            
            week_days.append({
                'date': day_date,
                'tasks': day_tasks,
                'events': day_events
            })
            
        # Hours for the week view
        hours = range(8, 21)  # 8 AM to 8 PM
    
    # For day view
    if view_type == 'day':
        # Get tasks for selected day
        day_tasks = Task.objects.filter(deadline__date=selected_date)
        
        # Get events for selected day
        try:
            from events.models import Event
            day_events = Event.objects.filter(date=selected_date)
        except:
            day_events = []
        
        # Calculate next and previous days
        prev_day = selected_date - timedelta(days=1)
        next_day = selected_date + timedelta(days=1)
        
        # Hours for the day view
        hours = range(8, 21)  # 8 AM to 8 PM
        
        # Get day note (if you have a DayNote model)
        day_note = ""  # Placeholder, replace with actual data if available
    
    # Get projects for task creation modal
    try:
        projects = Project.objects.all()
    except:
        projects = []
    
    context = {
        'today': today,
        'calendar_view': view_type,
        'current_month_name': current_month_name,
        'current_year': year,
        'current_month': month,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'selected_date': selected_date,
        'projects': projects,
    }
    
    # Add view-specific context
    if view_type == 'month':
        context.update({
            'calendar_weeks': calendar_weeks,
        })
    elif view_type == 'week':
        context.update({
            'week_days': week_days,
            'week_start': week_start,
            'week_end': week_end,
            'hours': hours,
        })
    elif view_type == 'day':
        context.update({
            'day_tasks': day_tasks,
            'day_events': day_events,
            'prev_day': prev_day,
            'next_day': next_day,
            'hours': hours,
            'day_note': day_note,
        })
    
    return render(request, 'tasks/calendar.html', context)

@login_required
def save_day_note(request):
    """View for saving day notes from the calendar"""
    if request.method == 'POST':
        note_text = request.POST.get('note', '')
        date_str = request.POST.get('date', '')
        
        try:
            note_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Here you would typically save the note to a database
            # For now, we'll just redirect back to the calendar with a success message
            messages.success(request, f'Note for {note_date.strftime("%B %d, %Y")} saved successfully!')
            
            return redirect('calendar')
        except ValueError:
            messages.error(request, 'Invalid date format provided.')
            return redirect('calendar')
    
    # If not a POST request, redirect to calendar view
    return redirect('calendar')
