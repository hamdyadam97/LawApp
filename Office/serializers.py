from rest_framework import serializers

from Office.models import Request, Case, LegalDocument, Document, Office
from User.models import User
from User.serializers import UserSerializer
from .utils import handle_document_upload


class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = [
            'id', 'status', 'request_type', 'description', 'user_id', 'case_id', 'created_at',
            'case_type', 'location', 'notes', 'plaintiff_name', 'defendant_name', 'national_address',
            'document_type', 'judgment_document_path', 'office_id','lawyer','case','user','office'
        ]
        read_only_fields = ['id', 'created_at']


# Serializer for Case model
class CaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = [
            'id', 'status', 'plaintiff_name', 'address', 'case_type', 'description',
            'date', 'time', 'notes', 'user', 'lawyer', 'office'
        ]
        read_only_fields = ['id', 'office', 'user']


class LegalDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalDocument
        fields = ['id', 'title', 'description', 'file', 'created_at','admin']
        read_only_fields = ['id', 'created_at']


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'filename', 'file', 'document_type', 'uploader', 'case', 'request', 'office', 'uploaded_at']
        read_only_fields = ['uploaded_at', 'id']


class CaseDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = ['id', 'date', 'time']


class CaseDateCreateSerializer(serializers.Serializer):
    case_id = serializers.IntegerField()
    date = serializers.DateField()
    time = serializers.TimeField()

    def validate_case_id(self, value):
        request = self.context['request']
        # Check if the case exists and belongs to the current lawyer
        try:
            case = Case.objects.get(id=value, lawyer_id=request.user.id)
        except Case.DoesNotExist:
            raise serializers.ValidationError("Case not found or not authorized")
        return value

class LawyerRequestSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    documents = DocumentSerializer(many=True)

    class Meta:
        model = Request
        fields = [
            'id', 'status', 'request_type', 'description', 'user', 'created_at',
            'case_type', 'location', 'notes', 'plaintiff_name', 'defendant_name', 'documents'
        ]



class ClientSerializer(serializers.ModelSerializer):
    cases = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'address', 'gender', 'cases']

    def get_cases(self, obj):
        # Filter cases specific to the logged-in lawyer
        lawyer_id = self.context['request'].user.id
        cases = obj.cases.filter(lawyer_id=lawyer_id)
        return CaseSerializer(cases, many=True).data



class CaseDateUpdateSerializer(serializers.ModelSerializer):
    date = serializers.DateField()
    time = serializers.TimeField()

    class Meta:
        model = Case
        fields = ['date', 'time']


class RequestDateUpdateSerializer(serializers.ModelSerializer):
    date = serializers.DateField()
    time = serializers.TimeField()

    class Meta:
        model = Request
        fields = ['date', 'time']



from rest_framework import serializers
from .models import Request, Document

class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ['status', 'notes', 'judgment_document_path']  # Add other fields as needed

    def validate_status(self, value):
        valid_statuses = ["pending", "in progress", "done", "reject"]
        if value not in valid_statuses:
            raise serializers.ValidationError("Invalid status")
        return value

    def create(self, validated_data):
        # Custom logic for handling document upload, if necessary
        document = validated_data.get('document')
        if document:
            # Assuming you have a custom file handling function
            doc = handle_document_upload(document, 'request', self.context['request'].user.id, 'lawyer', self.instance.id)
            validated_data['document'] = doc
        return super().create(validated_data)
