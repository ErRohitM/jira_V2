from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('api/notifications/', views.NotificationListView.as_view(), name='notification-list'),
    path('api/notifications/mark-read/', views.mark_notifications_read, name='mark-notifications-read'),
    path('api/notifications/preferences/', views.NotificationPreferenceView.as_view(), name='notification-preferences'),
    path('api/notifications/counts/', views.notification_counts, name='notification-counts'),
]