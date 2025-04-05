from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.urls import reverse_lazy

from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import Profile
from tasks.models import Task

class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')

class CustomPasswordChangeView(PasswordChangeView):
    success_url = reverse_lazy('profile')
    
    def form_valid(self, form):
        messages.success(self.request, 'Пароль успешно изменен!')
        return super().form_valid(form)

def register(request):
    if request.user.is_authenticated:
        return redirect('task_list')
        
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт создан для {username}! Теперь вы можете войти.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    completed_tasks_count = Task.objects.filter(owner=request.user, is_completed=True).count()
    active_tasks_count = Task.objects.filter(owner=request.user, is_completed=False).count()
    completion_percentage = 0
    
    if request.user.tasks.count() > 0:
        completion_percentage = (completed_tasks_count / request.user.tasks.count()) * 100
    
    context = {
        'completed_tasks_count': completed_tasks_count,
        'active_tasks_count': active_tasks_count,
        'completion_percentage': completion_percentage,
    }
    
    return render(request, 'users/profile.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Ваш профиль успешно обновлен!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
        
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    
    return render(request, 'users/edit_profile.html', context)
