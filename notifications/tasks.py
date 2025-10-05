from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from core.models import Tasks
from .services import notification_service

@shared_task
def send_overdue_reminders():
    """Send reminders for overdue issues"""
    now = timezone.now()

    # Find overdue issues that haven't been completed
    overdue_issues = Tasks.objects.filter(
        due_date__lt=now,
        status__in=['open', 'in_progress'],
        assigned_to__isnull=False
    ).select_related('assigned_to', 'project', 'project__organization')

    sent_count = 0
    for issue in overdue_issues:
        # Check if reminder was sent recently (within 24 hours)
        recent_reminder = issue.notifications.filter(
            notification_type='issue_overdue',
            created_at__gte=now - timedelta(hours=24)
        ).exists()

        if not recent_reminder:
            notification_service.send_overdue_reminder(issue)
            sent_count += 1

    return f"Sent {sent_count} overdue reminders"


@shared_task
def cleanup_old_notifications():
    """Clean up old read notifications"""
    cutoff_date = timezone.now() - timedelta(days=30)

    deleted_count = 0
    # Keep unread notifications, delete old read ones
    from .models import Notification
    result = Notification.objects.filter(
        is_read=True,
        read_at__lt=cutoff_date
    ).delete()

    if result[0]:
        deleted_count = result[0]

    return f"Deleted {deleted_count} old notifications"


@shared_task
def cleanup_inactive_websocket_connections():
    """Clean up inactive WebSocket connections"""
    cutoff_time = timezone.now() - timedelta(hours=1)

    from .models import WebSocketConnection
    result = WebSocketConnection.objects.filter(
        last_seen__lt=cutoff_time
    ).delete()

    deleted_count = result[0] if result[0] else 0
    return f"Cleaned up {deleted_count} inactive connections"


@shared_task
def send_daily_digest(user_id):
    """Send daily digest of unread notifications"""
    from django.contrib.auth.models import User
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from django.conf import settings

    try:
        user = User.objects.get(id=user_id)

        # Check if user has email notifications enabled
        try:
            prefs = user.notification_preferences
            if not prefs.email_enabled:
                return "Email notifications disabled for user"
        except:
            pass

        # Get unread notifications from last 24 hours
        yesterday = timezone.now() - timedelta(days=1)
        notifications = notification_service.get_user_notifications(
            user=user,
            unread_only=True
        ).filter(created_at__gte=yesterday)

        if not notifications.exists():
            return "No notifications to send"

        # Group notifications by organization/project
        context = {
            'user': user,
            'notifications': notifications,
            'total_count': notifications.count()
        }

        subject = f"Daily Digest - {notifications.count()} unread notifications"
        html_message = render_to_string('notifications/daily_digest.html', context)
        text_message = render_to_string('notifications/daily_digest.txt', context)

        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )

        return f"Sent daily digest to {user.email}"

    except User.DoesNotExist:
        return f"User {user_id} not found"
    except Exception as e:
        return f"Error sending digest: {str(e)}"
