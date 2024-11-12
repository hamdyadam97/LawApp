from django.urls import path
from . import views

app_name = 'invoice'

urlpatterns = [
    path('list/', views.GetInvoicesView.as_view(), name='invoice-list'),
    path('delete/<int:id>/', views.DeleteInvoiceView.as_view(), name='invoice-detail'),
    # path('legal-documents/', views.LegalDocumentListCreateView.as_view(), name='legal-doc-list-create'),
    # path('legal-documents/<int:pk>/', views.LegalDocumentDetailView.as_view(), name='legal-doc-detail'),
]
