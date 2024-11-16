from django.urls import path

from Invoice.views import GetInvoicesView, DeleteInvoiceView
from Notification.views import CreateListNotificationView, NotificationDetailView
from Office.views import RequestDetailView, ApproveRequestAPIView, DocumentCreateAPIView, \
    CreateUserDateView, LawyerRequestListView, CaseDateCreateView, RequestDateCreateView, LegalDocumentListCreateView, \
    CaseDocumentUploadView, UpdateRequestAPIView, RequestDetailsAPIView, RequestCreateView, RequestListView, \
    UserDatesAPIView, CaseDetailsView, UserCasesView, RequestUserCreateView, UserDocumentsView, CaseDocumentsView, \
    LawyerDatesAPIView, LawyerRequestsView, LawyerRequestDetailView
from User.views import AdminProfileView, LoginView, GetAllUsersView, UserProfileView, \
    LawyerDocumentListView, UserDetailsView, LawyerClientsListView, AdminUpdateProfileView, AdminUserUpdateProfileView, \
    AdminUserDeleteProfileView, AdminUserProfileCreate, AdminUserGetProfileView, UserDocumentListView, \
    UserUpdateProfileView, UserProfileCreate, LawyerProfileView, LawyerUpdateProfileView, LawyerUserProfileView

app_name = 'api'

urlpatterns = [
    path('admin/get_invoices/', GetInvoicesView.as_view(), name='invoice-list'),
    path('admin/delete_invoice/<int:id>/', DeleteInvoiceView.as_view(), name='invoice-delete'),
    path('admin/get_profile', AdminProfileView.as_view(), name='admin-profile-get'),
    path('lawyer_side/get_profile', LawyerProfileView.as_view(), name='lawyer-profile-get'),
    path('admin/update_profile', AdminUpdateProfileView.as_view(), name='admin-profile-update'),
    path('lawyer_side/profile', LawyerUpdateProfileView.as_view(), name='lawyer-profile-update'),
    path('admin/update_user/<int:pk>', AdminUserUpdateProfileView.as_view(), name='admin-user-update'),
    path('admin/delete_user/<int:pk>', AdminUserDeleteProfileView.as_view(), name='admin-user-delete'),
    path('admin/create_user/', AdminUserProfileCreate.as_view(), name='admin-user-profile-create'),
    path('superadmin/create_admin/', AdminUserProfileCreate.as_view(), name='super-admin-user-profile-create'),
    path('admin/add_lawyer/', AdminUserProfileCreate.as_view(), name='admin-lawyer-profile-create'),
    path('admin/get_users/', GetAllUsersView.as_view(), name='user-create'),
    ################################
    path('users/legaldocuments/', UserDocumentListView.as_view(), name='user-document-list'),
    path('users/profile/', UserUpdateProfileView.as_view(), name='user-update'),
    path('users/upload/', UserUpdateProfileView.as_view(), name='user-upload'),
    path('users/get_profile', UserProfileView.as_view(), name='user-profile-get'),
    path('users/cases/', UserCasesView.as_view(), name='user_cases'),
    path('lawyer_side/cases/', UserCasesView.as_view(), name='lawyer_cases'),
    path('users/dates', UserDatesAPIView.as_view(), name='user-date-get'),
    path('lawyer_side/dates', LawyerDatesAPIView.as_view(), name='user-date-get'),
    path('requests/', RequestListView.as_view(), name='request-list'),
    path('lawyer_side/requests/', LawyerRequestsView.as_view(), name='lawyer_requests'),
    path('request/<int:pk>/', RequestDetailView.as_view(), name='request-detail'),
    path('lawyer_side/<int:pk>/', LawyerRequestDetailView.as_view(), name='request-detail-lawyer'),
    path('lawyer_side/user/<int:pk>/', LawyerUserProfileView.as_view(), name='user-detail-lawyer'),
    path('requests/submit/', RequestUserCreateView.as_view(), name='request-create'),
    path('users/documents/', UserDocumentsView.as_view(), name='user_documents'),
    path('case/<int:case_id>/documents/', CaseDocumentsView.as_view(), name='case_documents'),
    path('lawyer_side/legaldocuments/', LawyerDocumentListView.as_view(), name='lawyer-document-list'),
    path('lawyer_side/lawyer_clients', LawyerClientsListView.as_view(), name='lawyer-clients-list'),
    ########################
    path('auth/signup/', UserProfileCreate.as_view(), name='user-create'),
    path('auth/login/', LoginView.as_view(), name='login'),
    ##########

    path('cases/<int:case_id>/', CaseDetailsView.as_view(), name='get_case_details'),
    ##############
    path('lawyers/<int:pk>', AdminUserGetProfileView.as_view(), name='admin-profile-get'),
    path('users/<int:pk>', AdminUserGetProfileView.as_view(), name='admin-profile-get'),
    path('users/detail', UserProfileView.as_view(), name='user-detail'),

    path('users/<int:user_id>/', UserDetailsView.as_view(), name='user-details'),

    path('admin/get_requests/', RequestListView.as_view(), name='request-list-create'),
    path('admin/create_request/', RequestCreateView.as_view(), name='request-create-admin'),
    path('admin/request/<int:pk>/', RequestDetailView.as_view(), name='request-detail-admin'),
    path("admin/approve/<int:request_id>/", ApproveRequestAPIView.as_view(), name="approve_request"),
    path('office/upload/', DocumentCreateAPIView.as_view(), name='upload_office_document'),
    path('date/', CreateUserDateView.as_view(), name='create-user-date'),
    path('lawyer-requests/', LawyerRequestListView.as_view(), name='lawyer-requests-list'),
    path('case/date/<int:case_id>/', CaseDateCreateView.as_view(), name='case-date-create'),
    path('request/date/<int:request_id>/', RequestDateCreateView.as_view(), name='request-date-create'),
    path('admin/legal-documents/', LegalDocumentListCreateView.as_view(), name='legal-doc-list-create'),
    path('case/upload/<int:case_id>/', CaseDocumentUploadView.as_view(), name='case-document-upload'),
    path('request/<int:request_id>/', UpdateRequestAPIView.as_view(), name='update-request'),
    path('request_details/<int:request_id>/', RequestDetailsAPIView.as_view(), name='request-details'),
    path('notifications/', CreateListNotificationView.as_view(), name='notification-list-create'),
    path('notifications/<int:pk>/', NotificationDetailView.as_view(), name='notification_detail'),
]
