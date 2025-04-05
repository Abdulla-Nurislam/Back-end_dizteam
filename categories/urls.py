from django.urls import path
from . import views

urlpatterns = [
    path('', views.CategoryListView.as_view(), name='category_list'),
    path('new/', views.CategoryCreateView.as_view(), name='category_create'),
    path('<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
]