from django.urls import path
from . import views


app_name = 'office'

urlpatterns = [
    path('requests/', views.RequestListCreateView.as_view(), name='request-list-create'),
    path('requests/<int:pk>/', views.RequestDetailView.as_view(), name='request-detail'),
    path("approve/<int:request_id>/",views.ApproveRequestAPIView.as_view(), name="approve_request"),
    path('office/upload/', views.DocumentCreateAPIView.as_view(), name='upload_office_document'),
    path('date/', views.CreateUserDateView.as_view(), name='create-user-date'),
    path('lawyer-requests/', views.LawyerRequestListView.as_view(), name='lawyer-requests-list'),
    path('case/date/<int:case_id>/', views.CaseDateCreateView.as_view(), name='case-date-create'),
    path('request/date/<int:request_id>/', views.RequestDateCreateView.as_view(), name='request-date-create'),
    path('legal-documents/', views.LegalDocumentListCreateView.as_view(), name='legal-doc-list-create'),
    path('case/upload/<int:case_id>/', views.CaseDocumentUploadView.as_view(), name='case-document-upload'),
    path('request/<int:request_id>/', views.UpdateRequestAPIView.as_view(), name='update-request'),
    path('request_details/<int:request_id>/', views.RequestDetailsAPIView.as_view(), name='request-details'),
]

