from django.urls import path
from . views import CreateUsersView, LoginView, logout_view

urlpatterns = [
    path('create_user/', CreateUsersView.as_view(), name='create-organization-user'),
    path('login/', LoginView.as_view(), name='user-login'),
    path('logout/', logout_view , name='logout'),
]