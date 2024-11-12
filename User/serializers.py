from django.contrib.auth.password_validation import validate_password
from django.utils.crypto import get_random_string
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from Office.models import Office

from .models import  User
# Serializer for Admin profile information
class UserProfileSerializer(serializers.ModelSerializer):
    refresh = serializers.CharField(read_only=True, source='token')
    access = serializers.CharField(read_only=True, source='token.access_token')

    def validate(self, attrs):
        # Extract usertype to check conditions
        usertype = attrs.get('usertype')

        if usertype == 'lawyer' or usertype == 'admin':
            # Ensure lawfirm is provided if usertype is 'lawyer' or 'admin'
            if not attrs.get('lawfirm'):
                raise serializers.ValidationError({"lawfirm": "This field is required for lawyers and admins."})
            attrs.pop('role', None)

        elif usertype == 'user':
            # Ensure role is provided if usertype is 'user'
            if not attrs.get('role'):
                raise serializers.ValidationError({"role": "This field is required for users."})
            attrs.pop('lawfirm', None)
        return attrs
    def validate_password(self, data):
        validate_password(data)
        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'address', 'phone', 'photo', 'lawfirm', 'office','role','user_type',
                  'access','refresh','password','id_document','address','country','is_email_verified',
                  'email_verification_code','dob','gender','is_active','is_deactivated','date_joined',
                  ]
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True},
            'email_verification_code': {'read_only': True},
            'is_active': {'read_only': True},
            'is_deactivated': {'read_only': True},
            'date_joined': {'read_only': True},
            'is_email_verified': {'read_only': True},


        }

# login user
class LoginSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        try:
            super().validate(attrs)
        except AuthenticationFailed:
            raise serializers.ValidationError("Incorrect email or password")

        # Customize the response data with user information if desired
        user = self.user
        return UserSerializer(instance=user, context=self.context).data




# Serializer for User model
class UserSerializer(serializers.ModelSerializer):
    refresh = serializers.CharField(read_only=True, source='token')
    access = serializers.CharField(read_only=True, source='token.access_token')


    def validate_password(self, data):
        validate_password(data)

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)

        return user

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'address', 'phone', 'photo', 'office',
                  'access', 'refresh', 'password', 'id_document', 'address', 'country', 'is_email_verified',
                  'email_verification_code', 'dob', 'gender', 'is_active', 'is_deactivated', 'date_joined',
                  ]
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True},
            'email_verification_code': {'read_only': True},
            'is_active': {'read_only': True},
            'is_deactivated': {'read_only': True},
            'date_joined': {'read_only': True},
            'is_email_verified': {'read_only': True},

        }

# Serializer for Lawyer model
class LawyerSerializer(serializers.ModelSerializer):
    refresh = serializers.CharField(read_only=True, source='token')
    access = serializers.CharField(read_only=True, source='token.access_token')


    def validate_password(self, data):
        validate_password(data)

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)

        return user

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'address', 'phone', 'photo', 'office',
                  'access', 'refresh', 'password', 'id_document', 'address', 'country', 'is_email_verified',
                  'email_verification_code', 'dob', 'gender', 'is_active', 'is_deactivated', 'date_joined',
                  ]
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True},
            'email_verification_code': {'read_only': True},
            'is_active': {'read_only': True},
            'is_deactivated': {'read_only': True},
            'date_joined': {'read_only': True},
            'is_email_verified': {'read_only': True},

        }

class CombinedUserSerializer(serializers.Serializer):
    clients = UserSerializer(many=True)
    lawyers = LawyerSerializer(many=True)


class OfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Office
        fields = ['id', 'office_name', 'address']
class UserDetailsSerializer(serializers.ModelSerializer):
    office = OfficeSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'id_document', 'phone', 'address',
            'role', 'gender', 'photo', 'office'
        ]


class UserOfficeProfileSerializer(serializers.ModelSerializer):
    refresh = serializers.CharField(read_only=True, source='token')
    access = serializers.CharField(read_only=True, source='token.access_token')
    office_name = serializers.CharField(write_only=True, required=False)  # New field for office name

    def validate(self, attrs):
        # Extract usertype to check conditions
        usertype = attrs.get('usertype')

        if usertype == 'lawyer' or usertype == 'admin':
            # Ensure lawfirm is provided if usertype is 'lawyer' or 'admin'
            if not attrs.get('lawfirm'):
                raise serializers.ValidationError({"lawfirm": "This field is required for lawyers and admins."})
            attrs.pop('role', None)

        elif usertype == 'user':
            # Ensure role is provided if usertype is 'user'
            if not attrs.get('role'):
                raise serializers.ValidationError({"role": "This field is required for users."})
            attrs.pop('lawfirm', None)

        # Check for office_name and create office if provided
        office_name = attrs.get('office_name')
        if office_name:
            office = Office.objects.create(name=office_name)
            attrs['office'] = office  # Associate the created office with the user

        return attrs

    def validate_password(self, data):
        validate_password(data)
        return data

    def create(self, validated_data):
        # Pop office_name from validated data to prevent duplication in User model
        office_name = validated_data.pop('office_name', None)

        # Create the user object
        user = User.objects.create_user(**validated_data)

        # Generate formkey for the user
        formkey = get_random_string(length=32)  # Generate a random formkey
        user.formkey = formkey
        user.save()

        return user

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'address', 'phone', 'photo', 'lawfirm', 'office', 'role', 'usertype',
                  'access', 'refresh', 'password', 'id_document', 'address', 'country', 'is_email_verified',
                  'email_verification_code', 'dob', 'gender', 'is_active', 'is_deactivated', 'date_joined', 'office_name']
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True},
            'email_verification_code': {'read_only': True},
            'is_active': {'read_only': True},
            'is_deactivated': {'read_only': True},
            'date_joined': {'read_only': True},
            'is_email_verified': {'read_only': True},
        }
