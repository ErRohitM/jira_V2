from rest_framework import serializers

from .models import Organization, Projects, Tasks
from users.models import BaseUser

class UserListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseUser
        fields = ['id', 'email']


class OrganizationSerializer(serializers.ModelSerializer):
    # For writing (POST/PUT)
    users = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=BaseUser.objects.all(),
        write_only=True
    )

    # For reading (GET)
    user_details = UserListingSerializer(source='users', many=True, read_only=True)

    class Meta:
        model = Organization
        fields = ['id', 'name', 'users', 'user_details']

    def validate_users(self, value):
        if not value:
            raise serializers.ValidationError("This field cannot be empty.")

        # Limit the number of related objects
        if len(value) > 5:
            raise serializers.ValidationError("You can only associate a maximum of 5 Users.")

        return value

class ProjectSerilizer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255, required=True)

    organization = serializers.PrimaryKeyRelatedField(
        many=False,
        queryset=Organization.objects.all(),
        write_only=True
    )
    # For reading (GET)
    organization_details = OrganizationSerializer(source='organization', many=False, read_only=True)

    status = serializers.ChoiceField(choices=Projects.STATUS_CHOICES, required=True)

    class Meta:
        model = Projects
        fields = ['id', 'name', 'description', 'organization', 'organization_details', 'status']

    def validate_organization(self, value):
        if not value:
            raise serializers.ValidationError("This field cannot be empty.")

        # Ensure all related objects exist
        organization = Organization.objects.filter(pk=value.id)
        if not organization:
            raise serializers.ValidationError(f"Organization {organization.name} do not exist.")

        return value

class TaskSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(
        many=False,
        queryset=Projects.objects.all(),
        write_only=True
    )
    project_details = ProjectSerilizer(source='project', many=False, read_only=True)

    title = serializers.CharField(max_length=200, required=True)
    type = serializers.ChoiceField(choices=Tasks.TASK_GROUP_CHOICES)

    priority = serializers.ChoiceField(choices=Tasks.PRIORITY_CHOICES, required=True)
    status = serializers.ChoiceField(choices=Tasks.STATUS_CHOICES, read_only=True)
    due_date = serializers.DateField(required=False)

    class Meta:
        model = Tasks
        fields = ['id', 'title', 'type', 'project', 'project_details', 'priority', 'status', 'due_date', 'attachments']

    def validate_project(self, value):
        if not value:
            raise serializers.ValidationError("This field cannot be empty.")

        # Ensure all related objects exist
        project = Projects.objects.filter(pk=value.id)
        if not project:
            raise serializers.ValidationError(f"Organization {project.name} do not exist.")

        return value