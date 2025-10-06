from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from core.models import Tasks
from users.models import BaseUser
from .models import NotificationPreference
from .services import notification_service


@receiver(post_save, sender=BaseUser)
def create_notification_preferences(sender, instance, created, **kwargs):
    """Create notification preferences for new users"""
    if created:
        NotificationPreference.objects.create(user=instance)


# @receiver(post_save, sender=Tasks)
# def handle_task_created(sender, instance, created, **kwargs):
#     """Handle task creation notifications"""
#     if created:
#         notification_service.create_task_notification(
#             task=instance,
#             notification_type='task_created',
#             sender=getattr(instance, '_created_by', None)
#         )


@receiver(pre_save, sender=Tasks)
def track_task_changes(sender, instance, **kwargs):
    """Track changes to task for notifications"""
    if instance.pk:
        try:
            old_instance = Tasks.objects.filter(pk=instance.pk)
            instance._old_assigned_to = old_instance.prefetch_related('assignees').values('assignees__email')
            instance._old_status = old_instance.values('status')
        except Tasks.DoesNotExist:
            pass


@receiver(post_save, sender=Tasks)
def handle_task_updated(sender, instance, created, **kwargs):
    """Handle task update notifications"""
    if not created:
        # Check if assigned user changed
        old_assigned_to = getattr(instance, '_old_assigned_to', None)
        if old_assigned_to != instance.assignees:
            notification_service.create_task_notification(
                task=instance,
                notification_type='task_assigned',
                sender=getattr(instance, '_updated_by', None)
            )

        # Check if status changed to completed
        old_status = getattr(instance, '_old_status', None)
        if old_status != instance.status and instance.status == 'DONE':
            notification_service.create_task_notification(
                task=instance,
                notification_type='task_completed',
                sender=getattr(instance, '_updated_by', None)
            )
        elif old_status != instance.status:  # Status update, changes on task work flow
            notification_service.create_task_notification(
                task=instance,
                notification_type='task_status_updated',
                sender=getattr(instance, '_updated_by', None)
            )
        # else:                                               # General update, changes on task work flow
        #     notification_service.create_task_notification(
        #         task=instance,
        #         notification_type='task_updated',
        #         sender=getattr(instance, '_updated_by', None)
        #     )

