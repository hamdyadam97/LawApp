from Notification.models import Notification


class NotificationService:
    @staticmethod
    def create_notification(message, notification_type, sender_id, sender_type, recipient_id, recipient_type, related_object_type, related_object_id):
        # Assuming a Notification model exists with the specified fields
        Notification.objects.create(
            message=message,
            notification_type=notification_type,
            sender_id=sender_id,
            sender_type=sender_type,
            recipient_id=recipient_id,
            recipient_type=recipient_type,
            related_object_type=related_object_type,
            related_object_id=related_object_id
        )


from .models import Document


def handle_document_upload(file, document_type, uploader_id, uploader_type, associated_id):
    try:
        # Create Document record in DB with file upload
        document = Document.objects.create(
            filename=file.name,
            file=file,  # Store the file using Django's FileField
            document_type=document_type,
            uploader_id=uploader_id,
            uploader_type=uploader_type,
            associated_id=associated_id
        )

        return document
    except Exception as e:
        return None
