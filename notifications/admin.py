from django.contrib import admin
from .models import Notification, NotificationPreference, WebSocketConnection


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipient', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at', 'organization', 'project']
    search_fields = ['title', 'message', 'recipient__username', 'recipient__email']
    readonly_fields = ['id', 'created_at', 'read_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'recipient', 'sender', 'organization', 'project', 'task'
        )


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_enabled', 'websocket_enabled', 'overdue_reminders', 'issue_updates']
    list_filter = ['email_enabled', 'websocket_enabled', 'overdue_reminders', 'issue_updates']
    search_fields = ['user__username', 'user__email']


@admin.register(WebSocketConnection)
class WebSocketConnectionAdmin(admin.ModelAdmin):
    list_display = ['user', 'organization', 'project', 'connected_at', 'last_seen']
    list_filter = ['organization', 'project', 'connected_at']
    search_fields = ['user__username', 'organization__name', 'project__name']
    readonly_fields = ['connected_at']

