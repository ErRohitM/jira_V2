from django.contrib.sessions.models import Session
from django.http import JsonResponse
from rest_framework import permissions
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.generics import ListCreateAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView

from users.authentication import CsrfExemptSessionAuthentication
from users.models import BaseUser

from . models import Organization, Projects, Tasks
from . serilizers import OrganizationSerializer, ProjectSerilizer, TaskSerializer


class CreateOrganizations(CreateAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication, SessionAuthentication)
    permission_classes = [permissions.IsAuthenticated] # object level custom permission can be used

class ListCreateProjects(ListCreateAPIView):
    queryset = Projects.objects.all()
    serializer_class = ProjectSerilizer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication, SessionAuthentication)
    permission_classes = [permissions.IsAuthenticated]  # object level custom permission can be used

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
                    return Projects.objects.filter(organization__users__id=user_id)
            except Session.DoesNotExist:
                pass  # Session does not exist
        return None  # Return None if no user is found


    def get(self, request, *args, **kwargs):
        user_credentials = self.get_query_set_from_user_session()
        serializer = self.serializer_class(user_credentials, many=True)
        return JsonResponse(serializer.data, safe=False, status=200)

class RetrieveUpdateDeleteProjects(ListCreateAPIView):
    queryset = Projects.objects.all()
    serializer_class = ProjectSerilizer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication, SessionAuthentication)
    permission_classes = [permissions.IsAuthenticated]  # object level custom permission can be used

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
                    return Projects.objects.filter(organization__users__id=user_id)
            except Session.DoesNotExist:
                pass  # Session does not exist
        return None  # Return None if no user is found


    def get(self, request, *args, **kwargs):
        user_credentials = self.get_query_set_from_user_session()
        serializer = self.serializer_class(user_credentials, many=True)
        return JsonResponse(serializer.data, safe=False, status=200)

class ListCreateTasks(ListCreateAPIView):
    queryset = Tasks.objects.all()
    serializer_class = TaskSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication, SessionAuthentication)
    permission_classes = [permissions.IsAuthenticated]  # object level custom permission can be used

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
                    return Tasks.objects.filter(project__organization__users__id=user_id)
            except Session.DoesNotExist:
                pass  # Session does not exist
        return None  # Return None if no user is found


    def get(self, request, *args, **kwargs):
        user_credentials = self.get_query_set_from_user_session()
        serializer = self.serializer_class(user_credentials, many=True)
        return JsonResponse(serializer.data, safe=False, status=200)

class RetriveUpdateDeleteTasks(RetrieveUpdateDestroyAPIView):
    queryset = Tasks.objects.all()
    serializer_class = TaskSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication, SessionAuthentication)
    permission_classes = [permissions.IsAuthenticated]  # object level custom permission can be used

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
                    return Tasks.objects.filter(project__organization__users__id=user_id)
            except Session.DoesNotExist:
                pass  # Session does not exist
        return None  # Return None if no user is found


    def get(self, request, *args, **kwargs):
        user_credentials = self.get_query_set_from_user_session()
        serializer = self.serializer_class(user_credentials, many=True)
        return JsonResponse(serializer.data, safe=False, status=200)

