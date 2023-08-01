from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .models import Heartbeat
from .serializers import HeartbeatSerializer
from chargepoint.models import Chargepoint
from drf_spectacular.openapi import AutoSchema


class HeartbeatApiView(GenericAPIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = HeartbeatSerializer
    schema = AutoSchema()

    def get_object(self, heartbeat_id):        
        # Helper method to get the object with given todo_id, and user_id

        try:
            return Heartbeat.objects.get(pk=heartbeat_id)
        except Heartbeat.DoesNotExist:
            return None

    # 5. Delete
    def delete(self, request, heartbeat_id, *args, **kwargs):
        '''
        Deletes the Heartbeat item with the given ID
        '''
        heartbeat = Heartbeat.objects.filter(pk=heartbeat_id)
        if not heartbeat:
            return Response(
                {"status": "Heartbeat with the given ID does not exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        heartbeat.delete()
        return Response(
            {"status": "Heartbeat deleted!"},
            status=status.HTTP_200_OK
        )


class HeartbeatSearchApiView(GenericAPIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = HeartbeatSerializer
    schema = AutoSchema()

    def get_object(self, chargepoint_id):        
        # Helper method to get the object with given todo_id, and user_id

        try:
            return Chargepoint.objects.get(pk=chargepoint_id)
        except Chargepoint.DoesNotExist:
            return None

    # 3. Retrieve
    def get(self, request, chargepoint_id, *args, **kwargs):
        '''
        Retrieves the Heartbeats of the given chargepoint
        '''
        cp_instance = self.get_object(chargepoint_id)
        if not cp_instance:
            return Response(
                {"status": "Chargepoint does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )

        heartbeats = Heartbeat.objects.filter(chargepoint__chargepoint_id=chargepoint_id)

        serializer = HeartbeatSerializer(heartbeats)
        return Response(serializer.data, status=status.HTTP_200_OK)
