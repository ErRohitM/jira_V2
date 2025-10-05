from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Notification, NotificationPreference
from .serializers import NotificationSerializer, NotificationPreferenceSerializer
from .services import notification_service

def home(request):
    return render(request, 'index.html')

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        organization_id = self.request.query_params.get('organization')
        project_id = self.request.query_params.get('project')
        unread_only = self.request.query_params.get('unread_only', 'false').lower() == 'true'

        return notification_service.get_user_notifications(
            user=user,
            organization_id=organization_id,
            project_id=project_id,
            unread_only=unread_only
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notifications_read(request):
    notification_ids = request.data.get('notification_ids', [])
    if not notification_ids:
        return Response({'error': 'notification_ids required'}, status=status.HTTP_400_BAD_REQUEST)

    count = notification_service.mark_notifications_read(notification_ids, request.user)
    return Response({'marked_read': count})


class NotificationPreferenceView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj, created = NotificationPreference.objects.get_or_create(user=self.request.user)
        return obj


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_counts(request):
    user = request.user
    organization_id = request.query_params.get('organization')
    project_id = request.query_params.get('project')

    total_unread = notification_service.get_user_notifications(
        user=user,
        organization_id=organization_id,
        project_id=project_id,
        unread_only=True
    ).count()

    return Response({
        'unread_count': total_unread
    })

