from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import BaseUser, UserTypeChoices


class CreateUserSerializer(serializers.ModelSerializer):
    """
    create user model object
    user type object can be created for manager / owner
    """
    user_type = serializers.ChoiceField(choices=UserTypeChoices, required=True)
    class Meta:
        model = BaseUser
        fields = ['first_name', 'middle_name', 'last_name', 'email', 'password', 'user_type']

        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        return BaseUser.objects.create_user(**validated_data)
        # # user type from validated data
        # if validated_data['user_type'] == UserTypeChoices.MANAGER or validated_data['user_type'] == UserTypeChoices.OWNER:
        #     return BaseUser.objects.create_superuser(**validated_data)
        # else:
        #     return BaseUser.objects.create_user(**validated_data)

class LoginUserSerializer(serializers.Serializer):
    email = serializers.CharField(label="Email", write_only=True)
    password = serializers.CharField(label="Password", style={'input_type': 'password'}, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError("Access denied: wrong username or password.")
        else:
            raise serializers.ValidationError("Both 'username' and 'password' are required.")

        attrs['user'] = user
        return attrs