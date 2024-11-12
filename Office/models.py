from idlelib.pyparse import trans

from django.db import models

from User.models import User


# Create your models here.


class Office(models.Model):
    office_name = models.CharField(max_length=100)
    address = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.office_name


class Case(models.Model):
    status = models.CharField(max_length=50, blank=True, null=True)
    plaintiff_name = models.CharField(max_length=100, blank=True, null=True)
    defendant_name = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    case_type = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    date = models.CharField(max_length=20, blank=True, null=True)
    time = models.CharField(max_length=10, blank=True, null=True)
    notes = models.JSONField(blank=True, null=True)
    user = models.ForeignKey('User.User', on_delete=models.SET_NULL, related_name="cases_user",null=True,blank=True)
    lawyer = models.ForeignKey('User.User', on_delete=models.SET_NULL, related_name="cases_lawyer", null=True, blank=True)
    office = models.ForeignKey(Office, on_delete=models.SET_NULL, related_name="cases_office", null=True, blank=True)

    def __str__(self):
        return f"Case {self.id} - {self.status}"


class Document(models.Model):
    filename = models.CharField(max_length=255)
    file = models.FileField(upload_to='case/Document',null=True,blank=True)
    document_type = models.CharField(max_length=50)
    uploader = models.ForeignKey('User.User', on_delete=models.CASCADE, related_name="documents_usser")
    case = models.ForeignKey(Case, on_delete=models.SET_NULL, related_name="documents_case", null=True, blank=True)
    request = models.ForeignKey("Request", on_delete=models.SET_NULL, related_name="documents_request", null=True, blank=True)
    office = models.ForeignKey(Office, on_delete=models.SET_NULL, related_name="documents_office", null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename


class Request(models.Model):
    status = models.CharField(max_length=100, default="Pending")
    request_type = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    case_type = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    notes = models.JSONField(default=list, blank=True, null=True)
    plaintiff_name = models.CharField(max_length=100, blank=True, null=True)
    defendant_name = models.CharField(max_length=100, blank=True, null=True)
    national_address = models.CharField(max_length=200, blank=True, null=True)
    document_type = models.CharField(max_length=100, blank=True, null=True)
    judgment_document_path = models.CharField(max_length=200, blank=True, null=True)
    user = models.ForeignKey('User.User', on_delete=models.CASCADE, related_name="requests_user",null=True,blank=True)
    case = models.ForeignKey(Case, on_delete=models.SET_NULL, related_name="requests_case", null=True, blank=True)
    office = models.ForeignKey(Office, on_delete=models.SET_NULL, related_name="requests_office", null=True, blank=True)
    lawyer = models.ForeignKey('User.User', on_delete=models.SET_NULL, related_name="requests_lawyer", null=True, blank=True)

    def __str__(self):
        return f"Request {self.id} - {self.status}"

class LegalDocument(models.Model):
        admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name="legal_documents_admin")
        title = models.CharField(max_length=100)
        description = models.CharField(max_length=255)
        file = models.FileField(upload_to='legal_documents',null=True)
        created_at = models.DateTimeField(auto_now_add=True,null=True)

        def to_dict(self):
            return {
                'id': self.id,
                'admin_id': self.admin.id,
                'title': self.title,
                'description': self.description,
                'file': self.file
            }

        def __str__(self):
            return self.title


class Event(models.Model):
    message = models.CharField(max_length=255)
    date = models.DateField()  # Storing the date separately as a DateField
    time = models.TimeField()  # Storing the time separately as a TimeField
 #   lawyer = models.ForeignKey('User.Lawyer', on_delete=models.CASCADE, related_name="events")
   # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events")#

    def __str__(self):
        return f"Event(id={self.id}, message='{self.message}', date='{self.date}', time='{self.time}')"