from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('list_notifications/', views.NotificationListView.as_view(), name='notification-list'),
    path('mark_notifications/mark-read/', views.mark_notifications_read, name='mark-notifications-read'),
    path('preferences_notifications/preferences/', views.NotificationPreferenceView.as_view(), name='notification-preferences'),
    path('count_notifications/counts/', views.notification_counts, name='notification-counts'),
]