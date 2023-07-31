from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
#from rest_framework.schemas.openapi import AutoSchema
import requests
from .serializers import *
from .tasks import *
from drf_spectacular.openapi import AutoSchema

class OcppResetApiView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OcppResetSerializer
    schema = AutoSchema()

    def post(self, request, *args, **kwargs):
        '''
        Send a Reset command (hard or soft)
        '''

        serializer = OcppResetSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.data["sync"]:
                task = ocpp16_reset_task(serializer.data["chargepoint_id"], serializer.data["reset_type"])
                return Response(task, status=status.HTTP_200_OK)
            else:
                task = ocpp16_reset_task.delay(serializer.data["chargepoint_id"], serializer.data["reset_type"]) # type: ignore
                return Response({"success": True, "status": "Task has been submitted successfully", "task_id": task.id}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OcppRemoteStartTrasactionApiView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OcppRemoteStartTransactionSerializer
    schema = AutoSchema()

    def post(self, request, *args, **kwargs):
        '''
        Send a Remote Start Transaction command
        '''

        serializer = OcppRemoteStartTransactionSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.data["sync"]:
                task = ocpp16_remote_start_transaction(serializer.data["chargepoint_id"], request.data["connector_id"], request.data["id_tag"], request.data.get("charging_profile", None))
                return Response(task, status=status.HTTP_200_OK)
            else:
                task = ocpp16_remote_start_transaction.delay(serializer.data["chargepoint_id"], request.data["connector_id"], request.data["id_tag"], request.data.get("charging_profile", None)) # type: ignore
                return Response({"success": True, "status": "Task has been submitted successfully", "task_id": task.id}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OcppRemoteStopTrasactionApiView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OcppRemoteStopTransactionSerializer
    schema = AutoSchema()

    def post(self, request, *args, **kwargs):
        '''
        Send a Remote Stop Transaction command
        '''

        serializer = OcppRemoteStopTransactionSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.data["sync"]:
                task = ocpp16_remote_stop_transaction(serializer.data["chargepoint_id"], serializer.data["transaction_id"])
                return Response(task, status=status.HTTP_200_OK)
            else:
                task = ocpp16_remote_stop_transaction.delay(serializer.data["chargepoint_id"], serializer.data["transaction_id"]) # type: ignore
                return Response({"success": True, "status": "Task has been submitted successfully", "task_id": task.id}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OcppReserveNowApiView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OcppReserveNowSerializer
    schema = AutoSchema()

    def post(self, request, *args, **kwargs):
        '''
        Send a Reserve Now command
        '''

        serializer = OcppReserveNowSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.data["sync"]:
                task = ocpp16_reserve_now(serializer.data["chargepoint_id"], serializer.data["connector_id"], serializer.data["id_tag"], serializer.data["expiry_date"], serializer.data["reservation_id"]) 
                return Response(task, status=status.HTTP_200_OK)
            else:
                task = ocpp16_reserve_now.delay(serializer.data["chargepoint_id"], serializer.data["connector_id"], serializer.data["id_tag"], serializer.data["expiry_date"], serializer.data["reservation_id"]) # type: ignore
                return Response({"success": True, "status": "Task has been submitted successfully", "task_id": task.id}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OcppCancelReservationApiView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OcppCancelReservationSerializer
    schema = AutoSchema()

    def post(self, request, *args, **kwargs):
        '''
        Send a Cancel Reservation command
        '''

        serializer = OcppCancelReservationSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.data["sync"]:
                task = ocpp16_cancel_reservation(serializer.data["chargepoint_id"], serializer.data["reservation_id"])
                return Response(task, status=status.HTTP_200_OK)
            else:
                task = ocpp16_cancel_reservation.delay(serializer.data["chargepoint_id"], serializer.data["reservation_id"]) # type: ignore
                return Response({"success": True, "status": "Task has been submitted successfully", "task_id": task.id}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OcppChangeAvailabilityApiView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OcppChangeAvailabilitySerializer
    schema = AutoSchema()

    def post(self, request, *args, **kwargs):
        '''
        Send a Change Availability command
        '''

        serializer = OcppChangeAvailabilitySerializer(data=request.data)
        if serializer.is_valid():
            if serializer.data["sync"]:
                task = ocpp16_change_availability(serializer.data["chargepoint_id"], serializer.data["connector_id"], serializer.data["availability_type"])
                return Response(task, status=status.HTTP_200_OK)
            else:
                task = ocpp16_change_availability.delay(serializer.data["chargepoint_id"], serializer.data["connector_id"], serializer.data["availability_type"]) # type: ignore
                return Response({"success": True, "status": "Task has been submitted successfully", "task_id": task.id}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OcppChangeConfigurationApiView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OcppChangeConfigurationSerializer
    schema = AutoSchema()

    def post(self, request, *args, **kwargs):
        '''
        Send a Change Configuration command
        '''

        serializer = OcppChangeConfigurationSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.data["sync"]:
                task = ocpp16_change_configuration(serializer.data["chargepoint_id"], serializer.data["key"], serializer.data["value"])
                return Response(task, status=status.HTTP_200_OK)
            else:
                task = ocpp16_change_configuration.delay(serializer.data["chargepoint_id"], serializer.data["key"], serializer.data["value"]) # type: ignore
                return Response({"success": True, "status": "Task has been submitted successfully", "task_id": task.id}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OcppClearCacheApiView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OcppCommandSerializer
    schema = AutoSchema()

    def post(self, request, *args, **kwargs):
        '''
        Send a Change Cache command
        '''

        serializer = OcppCommandSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.data["sync"]:
                task = ocpp16_clear_cache(serializer.data["chargepoint_id"])
                return Response(task, status=status.HTTP_200_OK)
            else:
                task = ocpp16_clear_cache.delay(serializer.data["chargepoint_id"]) # type: ignore
                return Response({"success": True, "status": "Task has been submitted successfully", "task_id": task.id}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OcppUnlockConnectorApiView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OcppUnlockConnectorSerializer
    schema = AutoSchema()

    def post(self, request, *args, **kwargs):
        '''
        Send an Unlock Connector command
        '''

        serializer = OcppUnlockConnectorSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.data["sync"]:
                task = ocpp16_unlock_connector(serializer.data["chargepoint_id"], serializer.data["connector_id"])
                return Response(task, status=status.HTTP_200_OK)
            else:
                task = ocpp16_unlock_connector.delay(serializer.data["chargepoint_id"], serializer.data["connector_id"]) # type: ignore
                return Response({"success": True, "status": "Task has been submitted successfully", "task_id": task.id}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OcppGetConfigurationApiView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OcppGetConfigurationSerializer
    schema = AutoSchema()

    def post(self, request, *args, **kwargs):
        '''
        Send a Get Configuration command
        '''

        serializer = OcppGetConfigurationSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.data["sync"]:
                task = ocpp16_get_configuration(serializer.data["chargepoint_id"], serializer.data["keys"])
                return Response(task, status=status.HTTP_200_OK)
            else:
                task = ocpp16_get_configuration.delay(serializer.data["chargepoint_id"], serializer.data["keys"]) # type: ignore
                return Response({"success": True, "status": "Task has been submitted successfully", "task_id": task.id}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OcppGetCompositeScheduleApiView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OcppGetCompositeScheduleSerializer
    schema = AutoSchema()

    def post(self, request, *args, **kwargs):
        '''
        Send a Get Composite Schedule command
        '''

        serializer = OcppGetCompositeScheduleSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.data["sync"]:
                task = ocpp16_get_composite_schedule_task(serializer.data["chargepoint_id"], serializer.data["connector_id"], serializer.data["duration"], serializer.data["charging_rate_unit_type"])
                return Response(task, status=status.HTTP_200_OK)
            else:
                task = ocpp16_get_composite_schedule_task.delay(serializer.data["chargepoint_id"], serializer.data["connector_id"], serializer.data["duration"], serializer.data["charging_rate_unit_type"]) # type: ignore
                return Response({"success": True, "status": "Task has been submitted successfully", "task_id": task.id}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OcppClearChargingProfileApiView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OcppClearChargingProfileSerializer
    schema = AutoSchema()

    def post(self, request, *args, **kwargs):
        '''
        Send a Clear Charging Profile command
        '''

        serializer = OcppClearChargingProfileSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.data["sync"]:
                task = ocpp16_clear_charging_profile_task(serializer.data["chargepoint_id"], serializer.data["charging_profile_id"], serializer.data["connector_id"], serializer.data["charging_profile_purpose_type"], serializer.data["stack_level"])
                return Response(task, status=status.HTTP_200_OK)
            else:
                task = ocpp16_clear_charging_profile_task.delay(serializer.data["chargepoint_id"], serializer.data["charging_profile_id"], serializer.data["connector_id"], serializer.data["charging_profile_purpose_type"], serializer.data["stack_level"]) # type: ignore
                return Response({"success": True, "status": "Task has been submitted successfully", "task_id": task.id}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    


class OcppSetChargingProfileApiView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OcppSetChargingProfileSerializer
    schema = AutoSchema()

    def post(self, request, *args, **kwargs):
        '''
        Send a Set Charging Profile command
        '''

        serializer = OcppSetChargingProfileSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.data["sync"]:
                task = ocpp16_set_charging_profile_task(serializer.data["chargepoint_id"], serializer.data["connector_id"], serializer.data["charging_profile_id"])
                return Response(task, status=status.HTTP_200_OK)
            else:
                task = ocpp16_set_charging_profile_task.delay(serializer.data["chargepoint_id"], serializer.data["connector_id"], serializer.data["charging_profile_id"]) # type: ignore
                return Response({"success": True, "status": "Task has been submitted successfully", "task_id": task.id}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
