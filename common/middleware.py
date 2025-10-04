from __future__ import unicode_literals
import threading

_user = threading.local()

class CurrentUserMiddleware:
    """Middleware to store the current user in thread-local storage."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _user.value = request.user if request.user.is_authenticated else None
        response = self.get_response(request)
        return response

def get_current_user():
    """Utility function to access the current user."""
    return getattr(_user, 'value', None)