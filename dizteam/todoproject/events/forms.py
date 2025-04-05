from django import forms
from .models import Event
from django.contrib.auth.models import User

class EventForm(forms.ModelForm):
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    repeat_until = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        input_formats=['%Y-%m-%d']
    )
    shared_with = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'select2'})
    )
    
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'start_time', 'end_time', 
            'location', 'all_day', 'repeat', 'repeat_until',
            'shared_with', 'notify_before'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'repeat': forms.Select(attrs={'class': 'form-select'}),
            'notify_before': forms.NumberInput(attrs={'min': 0, 'max': 1440})
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(EventForm, self).__init__(*args, **kwargs)
        
        if self.user:
            # Only show other users for sharing, not the current user
            self.fields['shared_with'].queryset = User.objects.exclude(id=self.user.id)
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        repeat = cleaned_data.get('repeat')
        repeat_until = cleaned_data.get('repeat_until')
        
        # Ensure end time is after start time
        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("End time must be after start time")
        
        # If repeating, require repeat_until
        if repeat != 'none' and not repeat_until:
            self.add_error('repeat_until', "Repeat until date is required for repeating events")
            
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if self.user and not instance.pk:  # If new event
            instance.owner = self.user
            
        if commit:
            instance.save()
            self.save_m2m()  # Save many-to-many relationships (shared_with)
            
        return instance 