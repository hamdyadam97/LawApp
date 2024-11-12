from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import CreateAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from User.models import User
from User.permission import AdminRequiredPermission
from .models import Notification
from .serializers import NotificationSerializer


class CreateListNotificationView(ListCreateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, AdminRequiredPermission]  # Ensure user is admin

    def perform_create(self, serializer):
        data = self.request.data
        recipient_id = data.get('recipient_id')
        recipient_type = data.get('recipient_type')

        # Validate recipient_type
        if recipient_type not in ['user', 'lawyer']:
            raise ValidationError({"error": "Invalid recipient type"})

        # Fetch the recipient based on recipient_type
        if recipient_type == 'user':
            recipient = User.objects.filter(id=recipient_id).first()
        elif recipient_type == 'lawyer':
            recipient = User.objects.filter(id=recipient_id).first()

        # Ensure the recipient exists and belongs to the same office as the sender
        if not recipient:
            raise NotFound({"error": f"{recipient_type.capitalize()} with id {recipient_id} not found"})

        if recipient.office_id != self.request.user.office_id:
            raise ValidationError(
                {"error": f"{recipient_type.capitalize()} with id {recipient_id} does not belong to the same office"})

        # Create notification
        notification = Notification(
            message=data['message'],
            sender=self.request.user,
            recipient=recipient,
            sender_type='admin',  # assuming sender type is always 'admin' in this case
            notification_type=data.get('notification_type', 'admin'),
            office_id=self.request.user.office_id,
            related_object_type=data.get('related_object_type'),
            related_object_id=data.get('related_object_id')
        )

        # Save the notification instance
        notification.save()

        return notification  # Returning the created notification for serialization
    def get_queryset(self):
        return Notification.objects.filter(office_id=self.request.user.office_id)

    def post(self, request, *args, **kwargs):
        # This is the entry point for handling POST requests.
        # First validate data using the serializer
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # If valid, create the notification
            notification = self.perform_create(serializer)
            return Response({
                "message": "Notification created successfully",
                "notification": NotificationSerializer(notification).data
            }, status=status.HTTP_201_CREATED)
        else:
            # If invalid, return the validation errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class NotificationDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, AdminRequiredPermission]

    def get(self, request, *args, **kwargs):
        """ Retrieve a single notification """
        notification = self.get_object()
        return Response(NotificationSerializer(notification).data)

    def patch(self, request, *args, **kwargs):
        """ Partially update a notification """
        notification = self.get_object()

        # Validate that the current user has permission to update the notification
        if notification.office_id != self.request.user.office_id:
            raise ValidationError({"error": "You do not have permission to update this notification"})

        serializer = self.get_serializer(notification, data=request.data, partial=True)  # Allow partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        """ Delete a notification """
        notification = self.get_object()

        # Ensure the notification belongs to the same office as the user
        if notification.office_id != self.request.user.office_id:
            raise ValidationError({"error": "You do not have permission to delete this notification"})

        notification.delete()
        return Response({"message": "Notification deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


