from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages

from .models import Category
from .forms import CategoryForm

class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'categories/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.all()

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'categories/category_form.html'
    success_url = reverse_lazy('category_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Категория успешно создана!')
        return super().form_valid(form)

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'categories/category_form.html'
    success_url = reverse_lazy('category_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Категория успешно обновлена!')
        return super().form_valid(form)

class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'categories/category_confirm_delete.html'
    success_url = reverse_lazy('category_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Категория успешно удалена!')
        return super().delete(request, *args, **kwargs)
