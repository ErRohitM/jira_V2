from rest_framework import serializers
from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    issue_title = serializers.CharField(source='issue.title', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'message', 'is_read',
            'created_at', 'read_at', 'sender', 'organization_name',
            'project_name', 'issue_title'
        ]
        read_only_fields = ['created_at', 'read_at']

    def get_sender(self, obj):
        if obj.sender:
            return {
                'id': obj.sender.id,
                'username': obj.sender.username,
                'full_name': obj.sender.get_full_name() or obj.sender.username
            }
        return None


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = ['email_enabled', 'websocket_enabled', 'overdue_reminders', 'issue_updates']
