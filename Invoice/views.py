from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from Invoice.models import Invoice
from Invoice.serializers import InvoiceSerializer
from User.permission import AdminRequiredPermission


class GetInvoicesView(APIView):
    permission_classes = [IsAuthenticated,AdminRequiredPermission]

    def get(self, request):
        # Assuming you have office_id in the User model
        invoices = Invoice.objects.filter(user__office_id=request.user.office_id)
        if not invoices:
            raise NotFound("No invoices found for the office.")

        serializer = InvoiceSerializer(invoices, many=True)
        return Response(serializer.data)


class DeleteInvoiceView(APIView):
    permission_classes = [IsAuthenticated,AdminRequiredPermission]

    def delete(self, request, id):
        # Fetch the invoice by ID, ensuring it belongs to the same office as the logged-in user
        invoice = Invoice.objects.filter(user__office_id=request.user.office_id, id=id).first()

        if not invoice:
            raise NotFound("Invoice not found")

        # Delete the invoice
        invoice.delete()

        return Response({"message": "Invoice deleted successfully"}, status=status.HTTP_200_OK)