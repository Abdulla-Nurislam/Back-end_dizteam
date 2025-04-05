from django import forms
from .models import Task
from categories.models import Category

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'category', 'is_completed']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(TaskForm, self).__init__(*args, **kwargs)
        
        # Обновляем queryset для категорий
        if self.user:
            # В будущем можно добавить фильтрацию по пользователю, если категории будут персональными
            self.fields['category'].queryset = Category.objects.all()
    
    def save(self, commit=True):
        instance = super(TaskForm, self).save(commit=False)
        if self.user and not instance.pk:  # Если новая задача
            instance.owner = self.user
        if commit:
            instance.save()
        return instance 