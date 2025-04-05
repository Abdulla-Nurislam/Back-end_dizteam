from django.core.management.base import BaseCommand
from django.utils import timezone
from events.models import Event
from tasks.models import Task
from events.utils import send_event_notification, send_task_deadline_notification, should_send_notification

class Command(BaseCommand):
    help = 'Send notifications for upcoming events and task deadlines'

    def handle(self, *args, **options):
        self.stdout.write('Starting notification check...')
        
        # Current time
        now = timezone.now()
        
        # Process event notifications
        upcoming_events = Event.objects.filter(
            start_time__gt=now,
            start_time__lt=now + timezone.timedelta(hours=24)
        )
        
        event_notifications_sent = 0
        for event in upcoming_events:
            if should_send_notification(event):
                # Send to owner
                send_event_notification(event, event.owner)
                event_notifications_sent += 1
                
                # Send to shared users
                for user in event.shared_with.all():
                    send_event_notification(event, user)
                    event_notifications_sent += 1
        
        # Process task deadline notifications
        upcoming_deadlines = Task.objects.filter(
            is_completed=False,
            deadline__isnull=False,
            deadline__gt=now,
            deadline__lt=now + timezone.timedelta(hours=24)
        )
        
        task_notifications_sent = 0
        for task in upcoming_deadlines:
            # Check if notification should be sent (30 minutes before deadline)
            notify_time = task.deadline - timezone.timedelta(minutes=30)
            if abs((now - notify_time).total_seconds()) < 300:  # 5 minutes window
                send_task_deadline_notification(task)
                task_notifications_sent += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully sent {event_notifications_sent} event notifications and '
            f'{task_notifications_sent} task deadline notifications.'
        )) 