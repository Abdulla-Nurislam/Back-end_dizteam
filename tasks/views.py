from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.utils import timezone

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
