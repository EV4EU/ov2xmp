from django.shortcuts import render
from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from statusnotification.models import Statusnotification
from statusnotification.serializers import StatusnotificationSerializer
from chargepoint.models import Chargepoint
from drf_spectacular.openapi import AutoSchema


class StatusnotificationApiView(GenericAPIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StatusnotificationSerializer
    schema = AutoSchema()

    # 5. Delete
    def delete(self, request, statusnotification_id, *args, **kwargs):
        '''
        Deletes the StatusNotification with given id, if exists
        '''
        statusnotification_instance = Statusnotification.objects.filter(pk=statusnotification_id)

        if not statusnotification_instance:
            return Response(
                {"status": "StatusNotification does not exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        statusnotification_instance.delete()
        return Response(
            {"status": "StatusNotification deleted!"},
            status=status.HTTP_200_OK
        )


class StatusnotificationSearchApiView(GenericAPIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StatusnotificationSerializer
    schema = AutoSchema()

    def get_object(self, chargepoint_id):        
        # Helper method to get the object with given todo_id, and user_id

        try:
            return Chargepoint.objects.get(chargepoint_id=chargepoint_id)
        except Statusnotification.DoesNotExist:
            return None

    # 3. Retrieve
    def get(self, request, chargepoint_id, *args, **kwargs):
        '''
        Retrieves the StatusNotifications belonging to the given chargepoint_id
        '''
        cp_instance = self.get_object(chargepoint_id=chargepoint_id)
        if not cp_instance:
            return Response(
                {"status": "Charge Point does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            statusnotification_objects = Statusnotification.objects.filter(connector__chargepoint__chargepoint_id=chargepoint_id)

        serializer = StatusnotificationSerializer(statusnotification_objects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
