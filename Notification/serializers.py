from rest_framework import serializers

from User.serializers import UserSerializer
from .models import Notification, User


class NotificationSerializer(serializers.ModelSerializer):
    sender_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='sender',  # Maps to sender relationship in Notification model
        write_only=True
    )
    recipient_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='recipient',  # Maps to recipient relationship in Notification model
        write_only=True
    )

    class Meta:
        model = Notification
        fields = [
            'id', 'message', 'created_at', 'is_read', 'notification_type',
            'sender', 'sender_type', 'recipient', 'recipient_type',
            'office_id', 'related_object_type', 'related_object_id',
            'sender_id', 'recipient_id'  # These fields will be writable
        ]
        read_only_fields = ['id', 'created_at', 'sender', 'recipient']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['sender'] = UserSerializer(instance.sender).data
        representation['recipient'] = UserSerializer(instance.recipient).data
        return representation
