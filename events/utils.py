from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.template.loader import render_to_string

def send_event_notification(event, user):
    """
    Send notification about upcoming event
    """
    subject = f"Upcoming event: {event.title}"
    event_url = reverse('event_detail', kwargs={'pk': event.pk})
    
    # Create absolute URL (this is a placeholder, customize based on your domain)
    base_url = "http://localhost:8000"  # In production, use your actual domain
    event_absolute_url = f"{base_url}{event_url}"
    
    # Create message with HTML and plain text versions
    html_message = render_to_string('events/email/event_notification.html', {
        'event': event,
        'user': user,
        'event_url': event_absolute_url
    })
    
    plain_message = f"""
    Hi {user.username},
    
    This is a reminder about your upcoming event:
    
    {event.title}
    
    Time: {event.start_time.strftime('%A, %B %d, %Y at %I:%M %p')}
    
    {f'Location: {event.location}' if event.location else ''}
    
    View details: {event_absolute_url}
    
    Regards,
    Todo App Team
    """
    
    # Send email
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@example.com',
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=True
    )
    
    return True

def send_task_deadline_notification(task):
    """
    Send notification about task deadline
    """
    subject = f"Task deadline reminder: {task.title}"
    task_url = reverse('task_detail', kwargs={'pk': task.pk})
    
    # Create absolute URL (this is a placeholder, customize based on your domain)
    base_url = "http://localhost:8000"  # In production, use your actual domain
    task_absolute_url = f"{base_url}{task_url}"
    
    # Create message with HTML and plain text versions
    html_message = render_to_string('tasks/email/task_deadline_notification.html', {
        'task': task,
        'user': task.owner,
        'task_url': task_absolute_url
    })
    
    plain_message = f"""
    Hi {task.owner.username},
    
    This is a reminder about your upcoming task deadline:
    
    {task.title}
    
    Deadline: {task.deadline.strftime('%A, %B %d, %Y at %I:%M %p')}
    
    {f'Project: {task.project.name}' if task.project else ''}
    {f'Area: {task.area.name}' if task.area else ''}
    
    View details: {task_absolute_url}
    
    Regards,
    Todo App Team
    """
    
    # Send email
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@example.com',
        recipient_list=[task.owner.email],
        html_message=html_message,
        fail_silently=True
    )
    
    return True

def should_send_notification(event):
    """
    Check if it's time to send notification for an event
    """
    now = timezone.now()
    notification_time = event.start_time - timezone.timedelta(minutes=event.notify_before)
    
    # Return True if current time is within 5 minute window of notification time
    # This handles cases where notification checking might not run exactly at notification time
    return abs((now - notification_time).total_seconds()) < 300  # 5 minutes window 