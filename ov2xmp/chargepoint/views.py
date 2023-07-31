from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .models import Chargepoint
from .serializers import ChargepointSerializer
from drf_spectacular.openapi import AutoSchema


class ChargepointApiView(GenericAPIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChargepointSerializer
    queryset = Chargepoint.objects.all()
    schema = AutoSchema()

    # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        List all the Chargepoints
        '''
        chargepoints = Chargepoint.objects.all()
        serializer = ChargepointSerializer(chargepoints, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request, *args, **kwargs):
        '''
        Create the Chargepoint with given data
        '''

        data = {
            'chargepoint_id': request.data.get('chargepoint_id'), 
            'chargepoint_serial_number': request.data.get('chargepoint_serial_number'), 
            'chargepoint_model': request.data.get('chargepoint_model'),
            'chargepoint_vendor': request.data.get('chargepoint_vendor'),
            'availability_status': request.data.get('availability_status'),
            'ocpp_version': request.data.get('ocpp_version')
        }

        serializer = ChargepointSerializer(data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChargepointDetailApiView(GenericAPIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChargepointSerializer
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
        Retrieves the Chargepoint with given chargepoint_id
        '''
        chargepoint_instance = self.get_object(chargepoint_id=chargepoint_id)
        if not chargepoint_instance:
            return Response(
                {"res": "Object with todo id does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ChargepointSerializer(chargepoint_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 4. Update
    def put(self, request, chargepoint_id, *args, **kwargs):
        '''
        Updates the Chargepoint item with given chargepoint_id, if exists
        '''
        chargepoint_instance = self.get_object(chargepoint_id)
        if not chargepoint_instance:
            return Response(
                {"res": "Object with todo id does not exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        data = {
            'chargepoint_id': request.data.get('chargepoint_id'), 
            'chargepoint_serial_number': request.data.get('chargepoint_serial_number'), 
            'chargepoint_model': request.data.get('chargepoint_model'),
            'chargepoint_vendor': request.data.get('chargepoint_vendor'),
            'ocpp_version': request.data.get('ocpp_version')
        }
        serializer = ChargepointSerializer(instance = chargepoint_instance, data=data, partial = True) # type: ignore
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 5. Delete
    def delete(self, request, chargepoint_id, *args, **kwargs):
        '''
        Deletes the Chargepoint item with given chargepoint_id, if exists
        '''
        chargepoint_instance = self.get_object(chargepoint_id)
        if not chargepoint_instance:
            return Response(
                {"res": "Object with todo id does not exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        chargepoint_instance.delete()
        return Response(
            {"res": "Object deleted!"},
            status=status.HTTP_200_OK
        )
