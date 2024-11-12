import logging

from django.http import Http404
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from Office.models import Request, LegalDocument, Case, Document, Office
from Office.serializers import RequestSerializer, LegalDocumentSerializer, DocumentSerializer, CaseDateCreateSerializer, \
    LawyerRequestSerializer, CaseDateUpdateSerializer, RequestDateUpdateSerializer

from User.permission import AdminRequiredPermission, LawyerRequiredPermission
from User.serializers import OfficeSerializer
from .utils import handle_document_upload


class RequestListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, AdminRequiredPermission]
    serializer_class = RequestSerializer

    def get_queryset(self):
        # Filter requests by the current admin's office
        return Request.objects.filter(office_id=self.request.user.office_id)


class RequestDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated, AdminRequiredPermission]  # Only authenticated admins can access

    def get_object(self):
        request_id = self.kwargs.get("request_id")
        try:
            req = Request.objects.get(id=request_id)
            if req.office_id != self.request.user.office_id:  # Check that office matches
                raise NotFound("Request not found")
            return req
        except Request.DoesNotExist:
            raise NotFound("Request not found")


class LegalDocumentListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, AdminRequiredPermission]
    serializer_class = LegalDocumentSerializer

    def get_queryset(self):
        # Only retrieve documents belonging to the current admin user
        return LegalDocument.objects.filter(admin_id=self.request.user.id)

    def perform_create(self, serializer):
        # Save with the current admin user as the owner
        serializer.save(admin_id=self.request.user.id)


class ApproveRequestAPIView(UpdateAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated, AdminRequiredPermission]  # Requires both authentication and admin status

    def get_queryset(self):
        # Retrieve the Request object based on request_id and ensure the user is authorized for their office
        request_id = self.kwargs['request_id']
        req = Request.objects.filter(id=request_id, office_id=self.request.user.office_id).first()
        if not req:
            raise Http404("Request not found or not in your office.")
        return req

    def perform_update(self, serializer):
        req = self.get_object()

        # Get the data from the request
        data = self.request.data
        date = data.get("date")
        time = data.get("time")
        lawyer_id = data.get("lawyer_id")

        # Create case data from the request instance
        case_data = {
            "status": "Open",
            "date": date,
            "time": time,
            "lawyer_id": lawyer_id,
        }

        request_attrs = [
            "plaintiff_name",
            "defendant_name",
            "national_address",
            "case_type",
            "description",
            "address",
            "notes",
            "document_type",
            "office_id",
            "user_id",
        ]

        for attr in request_attrs:
            value = getattr(req, attr, None)
            if value is not None:
                case_data["defendant" if attr == "defendant_name" else attr] = value

        judgment_document_paths = req.judgment_document_path
        if judgment_document_paths:
            case_data["judgment_document_path"] = judgment_document_paths

        # Create the new case
        new_case = Case.objects.create(**case_data)

        # Update the request's status and associate it with the new case
        req.status = "Approved"
        req.case_id = new_case.id
        req.save()

        # Save the updated request object with new case association
        serializer.save()

    def update(self, request, *args, **kwargs):
        # Call perform_update to process the case creation and request update
        self.perform_update(self.get_serializer())
        return Response({"message": "Request approved and case created successfully"}, status=status.HTTP_200_OK)


from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from .models import Document
from .serializers import DocumentSerializer


class DocumentCreateAPIView(CreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def perform_create(self, serializer):
        # Get the file from the request
        file = self.request.FILES.get('document')

        if not file:
            raise ValueError("No document uploaded")

        # Get the necessary fields from the request (e.g., user)
        uploader = self.request.user  # Assuming the user is authenticated
        document_type = self.request.data.get('document_type', 'office')  # Default to 'office' type

        # If you need to assign the file to a particular case, request, or office:
        associated_id = self.request.data.get('associated_id')
        associated_type = self.request.data.get('associated_type')

        # Here, you would need to handle file uploads and assignments
        document = serializer.save(
            filename=file.name,
            file=file,
            uploader=uploader,
            document_type=document_type,
        )

        # Assign additional fields based on the document_type
        if associated_type == 'request':
            document.request_id = associated_id
        elif associated_type == 'case':
            document.case_id = associated_id
        elif associated_type == 'office':
            document.office_id = associated_id

        document.save()

    def create(self, request, *args, **kwargs):
        # Optionally, add any pre-save checks or logging
        try:
            # Call the parent class’s create method to save the document
            return super().create(request, *args, **kwargs)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "An error occurred while uploading the document"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateUserDateView(APIView):
    permission_classes = [IsAuthenticated, LawyerRequiredPermission]

    def post(self, request):
        serializer = CaseDateCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            case_id = serializer.validated_data['case_id']
            date = serializer.validated_data['date']
            time = serializer.validated_data['time']

            # Retrieve the case and update its date and time
            case = Case.objects.get(id=case_id)
            case.date = date
            case.time = time
            case.save()

            return Response({"message": "Date created successfully"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LawyerRequestListView(ListAPIView):
    serializer_class = LawyerRequestSerializer
    permission_classes = [IsAuthenticated, LawyerRequiredPermission]

    def get_queryset(self):
        # Filter requests by the current lawyer's ID
        return Request.objects.filter(lawyer_id=self.request.user.id)





class CaseDateCreateView(CreateAPIView):
    serializer_class = CaseDateUpdateSerializer
    permission_classes = [IsAuthenticated, LawyerRequiredPermission]

    def post(self, request, case_id, *args, **kwargs):
        try:
            case = Case.objects.get(id=case_id, lawyer_id=request.user.id)
        except Case.DoesNotExist:
            return Response({"error": "Case not found or not authorized"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(case, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Create the notification
        NotificationService.create_notification(
            message=f"Date set for Case {case_id}: {serializer.validated_data['date']} at {serializer.validated_data['time']}",
            notification_type='system',
            sender_id=request.user.id,
            sender_type='lawyer',
            recipient_id=case.user_id,
            recipient_type='user',
            related_object_type='case',
            related_object_id=case_id
        )

        return Response({"message": "Date created successfully for Case"}, status=status.HTTP_201_CREATED)


class RequestDateCreateView(CreateAPIView):
    serializer_class = RequestDateUpdateSerializer
    permission_classes = [IsAuthenticated, LawyerRequiredPermission]

    def post(self, request, request_id, *args, **kwargs):
        try:
            req = Request.objects.get(id=request_id, lawyer_id=request.user.id)
        except Request.DoesNotExist:
            return Response({"error": "Request not found or not authorized"}, status=status.HTTP_404_NOT_FOUND)

        # Use the serializer to validate and save the date and time
        serializer = self.get_serializer(req, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Create the notification
        NotificationService.create_notification(
            message=f"Date set for Request {request_id}: {serializer.validated_data['date']} at {serializer.validated_data['time']}",
            notification_type='system',
            sender_id=request.user.id,
            sender_type='lawyer',
            recipient_id=req.user_id,
            recipient_type='user',
            related_object_type='request',
            related_object_id=request_id
        )

        return Response({"message": "Date created successfully for Request"}, status=status.HTTP_201_CREATED)



logger = logging.getLogger(__name__)


class CaseDocumentUploadView(APIView):
    permission_classes = [IsAuthenticated, LawyerRequiredPermission]

    def post(self, request, case_id, *args, **kwargs):
        logger.info(f"Content-Type: {request.content_type}")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request headers: {dict(request.headers)}")

        try:
            case = Case.objects.get(id=case_id)
            if case.lawyer_id != request.user.id:
                return Response({"error": "Case not found or not authorized"}, status=status.HTTP_404_NOT_FOUND)

            # Check if file is provided
            if 'file' not in request.FILES:
                return Response({"error": "No file part"}, status=status.HTTP_400_BAD_REQUEST)

            file = request.FILES['file']
            if file.name == "":
                return Response({"error": "No selected file"}, status=status.HTTP_400_BAD_REQUEST)

            # Handle file upload
            document = handle_document_upload(file, document_type='case', uploader_id=request.user.id,
                                              uploader_type='lawyer', associated_id=case_id)

            if document:
                logger.info(f"Document uploaded: {document.file.url}")  # Get the file URL

                # Send notification to the user
                notification_data = {
                    "message": f"New document uploaded for case {case_id}",
                    "sender_id": request.user.id,
                    "sender_type": 'lawyer',
                    "recipient_id": case.user_id,  # Notify the user associated with the case
                    "recipient_type": 'user',
                    "notification_type": 'new_case_document',
                    "related_object_type": 'case',
                    "related_object_id": case_id
                }
                NotificationService.create_notification(**notification_data)

                return Response({"message": "File uploaded successfully", "document_id": document.id},
                                status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Invalid file"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error uploading document: {str(e)}", exc_info=True)
            return Response({"error": "An error occurred while uploading the document"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateRequestAPIView(APIView):
    permission_classes = [IsAuthenticated, LawyerRequiredPermission]

    def patch(self, request, request_id, *args, **kwargs):
        request_item = Request.objects.filter(id=request_id, lawyer_id=request.user.id).first()

        if not request_item:
            return Response({"error": "Request not found or not authorized"}, status=status.HTTP_404_NOT_FOUND)

        # Deserialize the request data
        serializer = RequestSerializer(request_item, data=request.data, partial=True)

        if serializer.is_valid():
            # If there is any file to upload, handle it
            if 'document' in request.FILES:
                file = request.FILES['document']
                doc = handle_document_upload(file, 'request', request.user.id, 'lawyer', request_id)
                if not doc:
                    return Response({"error": "Invalid file"}, status=status.HTTP_400_BAD_REQUEST)

            # Commit changes to the database
            serializer.save()

            # Optionally, handle case status update or any other custom logic
            if 'status' in request.data:
                new_status = request.data['status']
                if request_item.case_id:
                    case = Case.objects.filter(id=request_item.case_id).first()
                    if case:
                        case.status = new_status
                        case.save()

            return Response({
                "message": "Request updated successfully",
                "request": serializer.data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class RequestDetailsAPIView(APIView):
    permission_classes = [IsAuthenticated, LawyerRequiredPermission]

    def get(self, request, request_id, *args, **kwargs):
        # Fetch the request object by ID and check if the lawyer is the one associated with the request
        request_obj = Request.objects.filter(id=request_id, lawyer_id=request.user.id).first()

        if not request_obj:
            return Response({"error": "Request not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)

        try:
            office = Office.objects.get(id=request_obj.office_id)
        except Office.DoesNotExist:
            return Response({"error": "Office not found"}, status=status.HTTP_404_NOT_FOUND)

        # Prepare the data for serialization
        result = RequestSerializer(request_obj).data
        result['office'] = OfficeSerializer(office).data  # Adding office data manually since it's related
        return Response(result, status=status.HTTP_200_OK)