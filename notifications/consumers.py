import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.template.loader import get_template, render_to_string

from core.models import Organization, Projects
from .models import WebSocketConnection, NotificationPreference


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        self.organization_id = self.scope['url_route']['kwargs']['organization_id']
        self.project_id = self.scope['url_route']['kwargs'].get('project_id')

        # Check if user has access to organization
        has_access = await self.check_organization_access()
        if not has_access:
            await self.close()
            return

        # Join organization group
        self.organization_group_name = f'org_{self.organization_id}'
        await self.channel_layer.group_add(
            self.organization_group_name,
            self.channel_name
        )

        # Join project group if specified
        if self.project_id:
            has_project_access = await self.check_project_access()
            if has_project_access:
                self.project_group_name = f'project_{self.project_id}'
                await self.channel_layer.group_add(
                    self.project_group_name,
                    self.channel_name
                )

        # Store connection
        await self.store_connection()

        await self.accept()

    async def disconnect(self, close_code):
        # Remove from groups
        await self.channel_layer.group_discard(
            self.organization_group_name,
            self.channel_name
        )

        if hasattr(self, 'project_group_name'):
            await self.channel_layer.group_discard(
                self.project_group_name,
                self.channel_name
            )

        # Remove connection record
        await self.remove_connection()

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'mark_notifications_read':
            notification_ids = data.get('notification_ids', [])
            await self.mark_notifications_read(notification_ids)
        elif message_type == 'join_project':
            project_id = data.get('project_id')
            await self.join_project_room(project_id)
        elif message_type == 'leave_project':
            project_id = data.get('project_id')
            await self.leave_project_room(project_id)

    async def notification_message(self, event):
        """Handle notification messages sent to the group"""
        notification_data = event['notification_data']

        # Check if user should receive this notification
        should_receive = await self.should_receive_notification(notification_data)
        if should_receive:

            html = get_template("partials/notification.html").render(
                context={"data": notification_data}
            )
            await self.send(text_data=html)

    async def issue_update(self, event):
        """Handle issue update messages"""
        issue_data = event['issue_data']
        await self.send(text_data=json.dumps({
            'type': 'issue_update',
            'data': issue_data
        }))

    @database_sync_to_async
    def check_organization_access(self):
        try:
            org = Organization.objects.get(id=self.organization_id)
            return org.users.filter(id=self.user.id).exists()
        except Organization.DoesNotExist:
            return False

    @database_sync_to_async
    def check_project_access(self):
        try:
            project = Projects.objects.get(id=self.project_id)
            return  project.organization.users.filter(id=self.user.id).exists()
        except Projects.DoesNotExist:
            return False

    @database_sync_to_async
    def store_connection(self):
        organization = Organization.objects.get(id=self.organization_id)
        project = None
        if self.project_id:
            project = Projects.objects.get(id=self.project_id)

        WebSocketConnection.objects.update_or_create(
            user=self.user,
            channel_name=self.channel_name,
            organization=organization,
            defaults={
                'project': project
            }
        )

    @database_sync_to_async
    def remove_connection(self):
        WebSocketConnection.objects.filter(
            user=self.user,
            channel_name=self.channel_name
        ).delete()

    @database_sync_to_async
    def mark_notifications_read(self, notification_ids):
        from .models import Notification
        from django.utils import timezone

        Notification.objects.filter(
            id__in=notification_ids,
            recipient=self.user
        ).update(is_read=True, read_at=timezone.now())

    @database_sync_to_async
    def should_receive_notification(self, notification_data):
        try:
            prefs = NotificationPreference.objects.get(user=self.user)
            return prefs.websocket_enabled and prefs.issue_updates
        except NotificationPreference.DoesNotExist:
            return True

    async def join_project_room(self, project_id):
        if await self.check_specific_project_access(project_id):
            group_name = f'project_{project_id}'
            await self.channel_layer.group_add(group_name, self.channel_name)
            await self.send(text_data=json.dumps({
                'type': 'joined_project',
                'project_id': project_id
            }))

    async def leave_project_room(self, project_id):
        group_name = f'project_{project_id}'
        await self.channel_layer.group_discard(group_name, self.channel_name)
        await self.send(text_data=json.dumps({
            'type': 'left_project',
            'project_id': project_id
        }))

    @database_sync_to_async
    def check_specific_project_access(self, project_id):
        try:
            project = Projects.objects.get(id=project_id)
            return project.members.filter(id=self.user.id).exists()
        except Projects.DoesNotExist:
            return False
