from django.shortcuts import render
from rest_framework import permissions, status, serializers
from rest_framework.exceptions import NotFound, APIException
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView, CreateAPIView, ListAPIView, \
    RetrieveAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from Office.models import LegalDocument, Case
from Office.serializers import LegalDocumentSerializer, CaseDateSerializer, CaseSerializer, ClientSerializer
from User.models import User
from User.permission import AdminRequiredPermission, LawyerRequiredPermission, IsSuperUser
from User.serializers import UserProfileSerializer, UserSerializer, LawyerSerializer, LoginSerializer, \
    UserDetailsSerializer


# Create your views here.
class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class AdminProfileCreate(CreateAPIView):
    serializer_class = UserProfileSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email', '')
        if User.objects.filter(email__iexact=email).exists():
            return Response({'detail': 'User with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        return self.create(request, *args, **kwargs)

# Admin Profile View (Retrieve and Update Admin)
class AdminProfileView(RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, AdminRequiredPermission]
    serializer_class = UserProfileSerializer

    def get_object(self):
        # If the user is an admin, the object is the admin's profile (request.user)
        user_id = self.request.query_params.get('id')
        if self.request.user.user_type == 'admin' and not user_id :
            return self.request.user

        # If it's a user or a lawyer, we need to fetch the object based on the provided ID

        if not user_id:

            raise NotFound('User ID must be provided for user/lawyer.')
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFound('User not found.')


class GetAllUsersView(APIView):
    permission_classes = [permissions.IsAuthenticated, AdminRequiredPermission]

    def get(self, request, *args, **kwargs):
        # Assume the current user is an Admin with an associated office
        office_id = request.user.office_id

        # Query both User and Lawyer models filtered by office
        users = User.objects.filter(office_id=office_id)
        clients = users.filter(user_type='user')
        lawyers = users.filter(user_type='lawyer')

        # Combine users and lawyers into one list and serialize
        user_serializer = UserProfileSerializer(users, many=True)
        lawyer_serializer = UserProfileSerializer(lawyers, many=True)
        combined_data = {
            "users": user_serializer.data,
            "lawyers": lawyer_serializer.data
        }

        return Response(combined_data, status=200)


class InvalidUserTypeException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid user type specified in URL."
    default_code = "invalid_user_type"


class UserProfileView(RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


class LawyerDocumentListView(ListAPIView):
    serializer_class = LegalDocumentSerializer
    permission_classes = [permissions.IsAuthenticated, LawyerRequiredPermission]

    def get_queryset(self):
        # Filter documents by the current user's ID
        return LegalDocument.objects.filter(admin_id=self.request.user.id)


class LawyerDatesListView(ListAPIView):
    serializer_class = CaseDateSerializer
    permission_classes = [permissions.IsAuthenticated, LawyerRequiredPermission]

    def get_queryset(self):
        # Filter cases by the current user's ID
        return Case.objects.filter(lawyer_id=self.request.user.id)


class LawyerListView(ListAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, LawyerRequiredPermission]

    def get_queryset(self):
        # Filter documents by the current user's ID
        return User.objects.filter(user_type='lawyer')


class UserDetailsView(RetrieveAPIView):
    serializer_class = UserDetailsSerializer
    permission_classes = [permissions.IsAuthenticated, LawyerRequiredPermission]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the lawyer is authorized to view the user's details
        if not Case.objects.filter(lawyer_id=request.user.id, user_id=user_id).exists():
            return Response({"error": "Not authorized to view this user's details"}, status=status.HTTP_403_FORBIDDEN)

        # Serialize the user details
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LawyerClientsListView(ListAPIView):
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated, LawyerRequiredPermission]
    def get_queryset(self):
        # Filter clients with cases associated with the current lawyer
        return User.objects.filter(cases__lawyer_id=self.request.user.id).distinct()


class AdminProfileCreate(APIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]  # Assuming the superadmin is already authenticated

    def post(self, request, *args, **kwargs):
        # Extract the email to check if the user already exists
        email = request.data.get('email', '')

        # Check if the user with the provided email already exists
        if User.objects.filter(email__iexact=email).exists():
            return Response({'detail': 'User with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        # If the user does not exist, proceed with user creation
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # This will create the user, office, and formkey

            return Response({
                'detail': 'User created successfully',
                'user_id': user.id,
                'formkey': user.formkey,  # Return the generated formkey
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)