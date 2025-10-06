from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sessions.models import Session
from django.db.models import Q
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Organization
from users.models import BaseUser
from .models import Notification, NotificationPreference
from .serializers import NotificationSerializer, NotificationPreferenceSerializer
from .services import notification_service

class HomeView(LoginRequiredMixin, View):
    def get_query_set_from_user_session(self):
        """
        Retrieve the user from the session using the session ID.
        """
        sessionid = self.request.COOKIES.get('sessionid')

        if sessionid:
            try:
                session = Session.objects.get(session_key=sessionid)
                session_data = session.get_decoded()
                user_id = session_data.get('_auth_user_id')

                if BaseUser.objects.filter(id=user_id).exists():
                    return user_id
                    # return Organization.objects.filter(users__id=user_id)
            except Session.DoesNotExist:
                pass  # Session does not exist
        return None  # Return None if no user is found

    def get(self, request, *args, **kwargs):
        # Fetch user ID from session
        user_id = self.get_query_set_from_user_session()

        if not user_id:
            return JsonResponse({'error': 'User session not found'}, status=400)

        # Fetch organizations related to the user with projects
        organizations = Organization.objects.prefetch_related('projects') \
                .filter(
                Q(users__id=user_id) &
                Q(id__isnull=False) &
                Q(projects__id__isnull=False)
            ).distinct()

        # Prepare context
        context = {
            "organizations": organizations.values_list('id', 'slug'),
            "projects": organizations.values_list('projects__id', 'projects__slug'),
        }

        return render(request, 'index.html', context)


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

