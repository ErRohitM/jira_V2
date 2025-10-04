from django.contrib import admin

from .models import Organization, Projects, Tasks

admin.site.register(Organization)
admin.site.register(Projects)
admin.site.register(Tasks)
