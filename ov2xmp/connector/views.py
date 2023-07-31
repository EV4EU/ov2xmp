from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .models import Connector
from .serializers import ConnectorSerializer
from drf_spectacular.openapi import AutoSchema


# Create your views here.
class ConnectorApiView(GenericAPIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ConnectorSerializer
    queryset = Connector.objects.all()
    schema = AutoSchema()

    # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        List all the Connectors
        '''
        connectors = Connector.objects.all()
        serializer = ConnectorSerializer(connectors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ConnectorDetailApiView(GenericAPIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ConnectorSerializer
    schema = AutoSchema()

    def get_objects(self, chargepoint_id):        
        try:
            return Connector.objects.filter(chargepoint__chargepoint_id=chargepoint_id).get()
        except Connector.DoesNotExist:
            return None
        
    def get_object(self, chargepoint_id, connector_id):        
        try:
            return Connector.objects.get(chargepoint__chargepoint_id=chargepoint_id, connectorid=connector_id )
        except Connector.DoesNotExist:
            return None

    # 3. Retrieve
    def get(self, request, chargepoint_id, *args, **kwargs):
        '''
        Retrieves the Connectors of the given chargepoint_id
        '''
        connector_instance = self.get_objects(chargepoint_id)
        if not connector_instance:
            return Response(
                {"res": "Object with todo id does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ConnectorSerializer(connector_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
