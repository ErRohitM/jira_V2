from django.urls import path

from . views import CreateOrganizations, ListCreateProjects, RetrieveUpdateDeleteProjects, ListCreateTasks, RetriveUpdateDeleteTasks

urlpatterns = [
    path('create_organizations/', CreateOrganizations.as_view(), name='list-create-organizations'),

    path('projects/', ListCreateProjects.as_view(), name='list-create-projects'),
    path('projects/<int:pk>/', RetrieveUpdateDeleteProjects.as_view(), name='retrieve-update-delete-projects'),

    path('tasks/', ListCreateTasks.as_view(), name='list-create-tasks'),
    path('tasks/<int:pk>/', RetriveUpdateDeleteTasks.as_view(), name='retrieve-update-delete-tasks'),
]