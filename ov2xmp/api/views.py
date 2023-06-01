from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.schemas.openapi import AutoSchema
import requests
from .serializers import *
from .tasks import *


class OcppResetApiView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OcppResetSerializer
    schema = AutoSchema(tags=['OCPP'])

    def post(self, request, *args, **kwargs):
        '''
        Send a Reset command (hard or soft)
        '''

        serializer = OcppResetSerializer(data=request.data)
        if serializer.is_valid():
            task = ocpp_reset_task.delay(serializer.data["reset_type"], serializer.data["chargepoint_url_identity"]) # type: ignore
            return Response({"success": True, "message": "Task has been submitted successfully", "task_id": task.id}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OcppRemoteStartTrasactionApiView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OcppRemoteStartTransactionSerializer
    schema = AutoSchema(tags=['OCPP'])

    def post(self, request, *args, **kwargs):
        '''
        Send a Remote Start Transaction command
        '''

        serializer = OcppRemoteStartTransactionSerializer(data=request.data)
        if serializer.is_valid():
            task = ocpp_remote_start_transaction.delay(serializer.data["chargepoint_url_identity"], request.data["connector_id"], request.data["id_tag"], request.data["charging_profile"]) # type: ignore
            return Response({"success": True, "message": "Task has been submitted successfully", "task_id": task.id}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OcppRemoteStopTrasactionApiView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OcppRemoteStopTransactionSerializer
    schema = AutoSchema(tags=['OCPP'])

    def post(self, request, *args, **kwargs):
        '''
        Send a Remote Stop Transaction command
        '''

        serializer = OcppRemoteStopTransactionSerializer(data=request.data)
        if serializer.is_valid():
            task = ocpp_remote_stop_transaction.delay(serializer.data["chargepoint_url_identity"], serializer.data["transaction_id"]) # type: ignore
            return Response({"success": True, "message": "Task has been submitted successfully", "task_id": task.id}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
