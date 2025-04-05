from django import forms
from .models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            # Проверка на существование категории с таким именем
            if Category.objects.filter(name__iexact=name).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Категория с таким именем уже существует.')
        return name 