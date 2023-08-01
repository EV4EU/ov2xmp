from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .models import Transaction
from .serializers import TransactionSerializer
from chargepoint.models import Chargepoint
from drf_spectacular.openapi import AutoSchema


class TransactionApiView(GenericAPIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()
    schema = AutoSchema()

    # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        List all the Transactions
        '''
        Transactions = Transaction.objects.all()
        serializer = TransactionSerializer(Transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TransactionDetailApiView(GenericAPIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TransactionSerializer
    schema = AutoSchema()

    def get_object(self, transaction_id):        
        # Helper method to get the object with given todo_id, and user_id

        try:
            return Transaction.objects.get(pk=transaction_id)
        except Transaction.DoesNotExist:
            return None

    # 3. Retrieve
    def get(self, request, transaction_id, *args, **kwargs):
        '''
        Retrieves the Transaction with given ID
        '''
        transaction_instance = self.get_object(transaction_id)
        if not transaction_instance:
            return Response(
                {"status": "Transaction with the given ID does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = TransactionSerializer(transaction_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


    # 5. Delete
    def delete(self, request, transaction_id, *args, **kwargs):
        '''
        Deletes the Transaction item with given id, if exists
        '''
        transaction_instance = self.get_object(transaction_id)
        if not transaction_instance:
            return Response(
                {"status": "Transaction with the given ID does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
        transaction_instance.delete()
        return Response(
            {"status": "Transaction deleted!"},
            status=status.HTTP_200_OK
        )


class TransactionSearchApiView(GenericAPIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TransactionSerializer
    schema = AutoSchema()

    def get_object(self, chargepoint_id):        
        try:
            return Chargepoint.objects.get(pk=chargepoint_id)
        except Chargepoint.DoesNotExist:
            return None

    # 3. Retrieve
    def get(self, request, chargepoint_id, *args, **kwargs):
        '''
        Retrieves the Transactions belonging to the given ID
        '''
        cp_instance = self.get_object(chargepoint_id)
        if not cp_instance:
            return Response(
                {"status": "Chargepoint with the given ID does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
        transaction_object = Transaction.objects.filter(connector__chargepoint__chargepoint_id=chargepoint_id)
        serializer = TransactionSerializer(transaction_object, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
