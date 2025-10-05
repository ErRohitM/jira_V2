from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification, NotificationPreference
from django.utils import timezone


class NotificationService:
    def __init__(self):
        self.channel_layer = get_channel_layer()

    def create_task_notification(self, task, notification_type, sender=None, message=None):
        """Create notification for task events"""

        # Get all project members
        project_members = task.project.organization.users.all()

        # Create notifications for each member
        notifications = []
        for member in project_members:
            # Skip sender to avoid self-notification
            if sender and member == sender:
                continue

            # Check user preferences
            try:
                prefs = NotificationPreference.objects.get(user=member)
                if not prefs.task_updates:
                    continue
            except NotificationPreference.DoesNotExist:
                pass  # Default to sending notifications

            notification = Notification.objects.create(
                recipient=member,
                sender=sender,
                organization=task.project.organization,
                project=task.project,
                task=task,
                notification_type=notification_type,
                title=self._get_notification_title(notification_type, task),
                message=message or self._get_notification_message(notification_type, task, sender)
            )
            notifications.append(notification)

        # Send WebSocket notifications
        self._send_websocket_notifications(notifications)

        return notifications

    def send_overdue_reminder(self, task):
        """Send overdue reminder for an task"""
        if not task.assigned_to:
            return None

        # Check user preferences
        try:
            prefs = NotificationPreference.objects.get(user=task.assigned_to)
            if not prefs.overdue_reminders:
                return None
        except NotificationPreference.DoesNotExist:
            pass

        notification = Notification.objects.create(
            recipient=task.assigned_to,
            organization=task.project.organization,
            project=task.project,
            task=task,
            notification_type='task_overdue',
            title=f'Overdue: {task.title}',
            message=f'Issue "{task.title}" is overdue. Due date was {task.due_date}.'
        )

        # Send WebSocket notification
        self._send_websocket_notifications([notification])

        return notification

    def _get_notification_title(self, notification_type, task):
        titles = {
            'task_created': f'New Issue: {task.title}',
            'task_updated': f'Issue Updated: {task.title}',
            'task_assigned': f'Issue Assigned: {task.title}',
            'task_completed': f'Issue Completed: {task.title}',
            'task_overdue': f'Overdue: {task.title}',
        }
        return titles.get(notification_type, f'Issue Notification: {task.title}')

    def _get_notification_message(self, notification_type, task, sender):
        sender_name = sender.get_full_name() or sender.username if sender else 'System'
        messages = {
            'task_created': f'{sender_name} created a new task in {task.project.name}',
            'task_updated': f'{sender_name} updated the task in {task.project.name}',
            'task_assigned': f'You have been assigned to this task in {task.project.name}',
            'task_completed': f'{sender_name} completed the task in {task.project.name}',
            'task_overdue': f'Issue is overdue in {task.project.name}',
        }
        return messages.get(notification_type, f'Issue notification from {sender_name}')

    def _send_websocket_notifications(self, notifications):
        """Send notifications via WebSocket"""
        for notification in notifications:
            # Send to organization group
            org_group = f'org_{notification.organization.id}'
            project_group = f'project_{notification.project.id}'

            notification_data = {
                'id': str(notification.id),
                'type': notification.notification_type,
                'title': notification.title,
                'message': notification.message,
                'task_id': notification.task.id,
                'project_id': notification.project.id,
                'organization_id': notification.organization.id,
                'created_at': notification.created_at.isoformat(),
                'sender': {
                    'id': notification.sender.id,
                    'username': notification.sender.username,
                    'full_name': notification.sender.get_full_name()
                } if notification.sender else None
            }

            # Send to project group
            async_to_sync(self.channel_layer.group_send)(
                org_group,
                {
                    'type': 'notification_message',
                    'notification_data': notification_data
                }
            )

    def get_user_notifications(self, user, organization_id=None, project_id=None, unread_only=False):
        """Get notifications for a user"""
        queryset = Notification.objects.filter(recipient=user)

        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)

        if project_id:
            queryset = queryset.filter(project_id=project_id)

        if unread_only:
            queryset = queryset.filter(is_read=False)

        return queryset.select_related('sender', 'organization', 'project', 'task')

    def mark_notifications_read(self, notification_ids, user):
        """Mark notifications as read"""
        return Notification.objects.filter(
            id__in=notification_ids,
            recipient=user
        ).update(is_read=True, read_at=timezone.now())


# Global instance
notification_service = NotificationService()