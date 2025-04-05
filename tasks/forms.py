from django import forms
from .models import Task, Project, Area, Tag
from categories.models import Category
from events.models import Event

class TaskForm(forms.ModelForm):
    deadline = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'category', 'is_completed',
            'project', 'area', 'tags', 'deadline', 'today_flag', 'event'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'tags': forms.SelectMultiple(attrs={'class': 'select2'}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'area': forms.Select(attrs={'class': 'form-select'}),
            'event': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(TaskForm, self).__init__(*args, **kwargs)
        
        if self.user:
            # Filter objects by user
            self.fields['category'].queryset = Category.objects.all()  # Categories are global for now
            self.fields['project'].queryset = Project.objects.filter(owner=self.user)
            self.fields['area'].queryset = Area.objects.filter(owner=self.user)
            self.fields['tags'].queryset = Tag.objects.filter(owner=self.user)
            self.fields['event'].queryset = Event.objects.filter(
                owner=self.user
            ).order_by('start_time')
    
    def save(self, commit=True):
        instance = super(TaskForm, self).save(commit=False)
        if self.user and not instance.pk:  # If new task
            instance.owner = self.user
        if commit:
            instance.save()
            self.save_m2m()  # Save tags
        return instance

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class TagForm(forms.ModelForm):
    color = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
        required=True
    )
    
    class Meta:
        model = Tag
        fields = ['name', 'color'] 