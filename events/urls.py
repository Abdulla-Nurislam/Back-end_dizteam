from django.urls import path
from . import views

urlpatterns = [
    # Event management
    path('', views.EventListView.as_view(), name='event_list'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('api/events/', views.get_calendar_events, name='get_calendar_events'),
    path('<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('create/', views.EventCreateView.as_view(), name='event_create'),
    path('<int:pk>/update/', views.EventUpdateView.as_view(), name='event_update'),
    path('<int:pk>/delete/', views.EventDeleteView.as_view(), name='event_delete'),
] 