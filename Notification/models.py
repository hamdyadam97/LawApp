from django.db import models
from Office.models import Office
from User.models import User


# Create your models here.


class Notification(models.Model):
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=50)
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_notifications')
    sender_type = models.CharField(max_length=50, blank=True, null=True)
    recipient = models.ManyToManyField(User, related_name='received_notifications')
    recipient_type = models.CharField(max_length=50)
    office = models.ForeignKey(Office, on_delete=models.SET_NULL, null=True, related_name='notifications')
    related_object_type = models.CharField(max_length=50, blank=True, null=True)
    related_object_id = models.IntegerField(blank=True, null=True)

    def to_dict(self):
        return {
            'id': self.id,
            'message': self.message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_read': self.is_read,
            'notification_type': self.notification_type,
            'sender_id': self.sender.id if self.sender else None,
            'sender_type': self.sender_type,
            'recipient_id': self.recipient.id,
            'recipient_type': self.recipient_type,
            'office_id': self.office.id if self.office else None,
            'related_object_type': self.related_object_type,
            'related_object_id': self.related_object_id
        }

    class Meta:
        db_table = 'notification'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'