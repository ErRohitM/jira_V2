from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login as django_login, logout
from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from .serializers import CreateUserSerializer, LoginUserSerializer
from . models import BaseUser
from . authentication import CsrfExemptSessionAuthentication

class CreateUsersView(CreateAPIView):
    queryset = BaseUser.objects.all()
    serializer_class = CreateUserSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication, SessionAuthentication)
    permission_classes = [permissions.IsAuthenticated]

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication, SessionAuthentication)
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        # Use the serializer to validate the login credentials
        serializer = LoginUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get the user from validated data
        user = serializer.validated_data['user']

        # Perform the login
        django_login(request, user)

        # Return login success response
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
            return Response("CookieAddUserCredentialsSentMailLogsSerializer is Added")
        return Response({
            'status': 'success',
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)

@csrf_exempt
def logout_view(request):
    logout(request)
    return JsonResponse({'success': 'Log out Successfully'})