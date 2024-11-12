from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('get-edit-destroy-profile/', views.AdminProfileView.as_view(), name='admin-profile'),
    path('create-profile/', views.AdminProfileCreate.as_view(), name='admin-profile-create'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('users/', views.GetAllUsersView.as_view(), name='user-create'),
    path('users/detail', views.UserProfileView.as_view(), name='user-detail'),
    path('legaldocuments/', views.LawyerDocumentListView.as_view(), name='lawyer-document-list'),
    path('users/<int:user_id>/', views.UserDetailsView.as_view(), name='user-details'),
    path('lawyer_clients/', views.LawyerClientsListView.as_view(), name='lawyer-clients-list'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

