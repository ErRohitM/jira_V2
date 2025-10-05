from django.conf import settings
from django.db import models
import uuid

from core.models import Organization, Projects, Tasks
from common.models import BaseModels

class NotificationPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_preferences')
    email_enabled = models.BooleanField(default=True)
    websocket_enabled = models.BooleanField(default=True)
    overdue_reminders = models.BooleanField(default=True)
    issue_updates = models.BooleanField(default=True)

    def __str__(self):
        return f"Preferences for {self.user.email}"


class Notification(BaseModels):
    NOTIFICATION_TYPES = (
        ('task_created', 'Task Created'),
        ('task_updated', 'Task Updated'),
        ('task_assigned', 'Task Assigned'),
        ('task_overdue', 'Task Overdue'),
        ('task_completed', 'Task Completed'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications_recipient')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications_sender', null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE)

    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()

    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['organization', 'project']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.recipient.email}"


class WebSocketConnection(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    channel_name = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, null=True, blank=True)
    connected_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'channel_name', 'organization']

    def __str__(self):
        return f"{self.user.first_name} - {self.organization.name}"
