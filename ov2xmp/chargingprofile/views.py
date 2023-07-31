from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .models import Chargingprofile
from .serializers import ChargingprofileSerializer
from drf_spectacular.openapi import AutoSchema


class ChargingprofileApiView(GenericAPIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChargingprofileSerializer
    queryset = Chargingprofile.objects.all()
    schema = AutoSchema()

    # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        List all the ChargingProfiles
        '''
        chargingprofiles = Chargingprofile.objects.all()
        serializer = ChargingprofileSerializer(chargingprofiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request, *args, **kwargs):
        '''
        Create the ChargingProfile with given data. Please note that chargingschedule_period accepts multiple JSON objects with the following keys: "startPeriod", "limit", "number_phases".
        '''
        print(request.data)

        data = {
            'chargingprofile_id': request.data.get('chargingprofile_id'), 
            'transaction_id': request.data.get('transaction_id', None),
            'stack_level': request.data.get('stack_level'), 
            'chargingprofile_purpose': request.data.get('chargingprofile_purpose'),
            'chargingprofile_kind': request.data.get('chargingprofile_kind'),
            'recurrency_kind': request.data.get('recurrency_kind', None),
            'valid_from': request.data.get('valid_from', None),
            'valid_to': request.data.get('valid_to', None),
            'valid_from': request.data.get('valid_from', None),
            'duration': request.data.get('duration', None),
            'start_schedule': request.data.get('start_schedule', None),
            'charging_rate_unit': request.data.get('charging_rate_unit'),
            'chargingschedule_period': request.data.get('chargingschedule_period'),
            'min_charging_rate': request.data.get('min_charging_rate', None)
        }

        serializer = ChargingprofileSerializer(data=data) # type: ignore
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChargingprofileDetailApiView(GenericAPIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChargingprofileSerializer
    schema = AutoSchema()

    def get_object(self, chargingprofile_id):        
        # Helper method to get the object with given todo_id, and user_id

        try:
            return Chargingprofile.objects.get(pk=chargingprofile_id)
        except Chargingprofile.DoesNotExist:
            return None

    # 3. Retrieve
    def get(self, request, chargingprofile_id, *args, **kwargs):
        '''
        Retrieves the ChargingProfile with given ID
        '''
        chargingprofile_instance = self.get_object(chargingprofile_id)
        if not chargingprofile_instance:
            return Response(
                {"res": "Object with todo id does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ChargingprofileSerializer(chargingprofile_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 4. Update
    def put(self, request, chargingprofile_id, *args, **kwargs):
        '''
        Updates the ChargingProfile item with given id, if exists. Please note that chargingschedule_period accepts multiple JSON objects with the following keys: "startPeriod", "limit", "number_phases".
        '''
        chargingprofile_instance = self.get_object(chargingprofile_id)
        if not chargingprofile_instance:
            return Response(
                {"res": "Object with todo id does not exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = {
            'chargingprofile_id': request.data.get('chargingprofile_id'), 
            'transaction_id': request.data.get('transaction_id', None),
            'stack_level': request.data.get('stack_level'), 
            'chargingprofile_purpose': request.data.get('chargingprofile_purpose'),
            'chargingprofile_kind': request.data.get('chargingprofile_kind'),
            'recurrency_kind': request.data.get('recurrency_kind', None),
            'valid_from': request.data.get('valid_from', None),
            'valid_to': request.data.get('valid_to', None),
            'duration': request.data.get('valid_from', None),
            'start_schedule': request.data.get('valid_from', None),
            'charging_rate_unit': request.data.get('valid_from'),
            'chargingschedule_period': request.data.get('chargingschedule_period'),
            'min_charging_rate': request.data.get('min_charging_rate', None)
        }
        serializer = ChargingprofileSerializer(instance=chargingprofile_instance, data=data, partial=True) # type: ignore
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 5. Delete
    def delete(self, request, chargingprofile_id, *args, **kwargs):
        '''
        Deletes the ChargingProfile item with given id, if exists
        '''
        chargingprofile_instance = self.get_object(chargingprofile_id)
        if not chargingprofile_instance:
            return Response(
                {"res": "Object with todo id does not exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        chargingprofile_instance.delete()
        return Response(
            {"res": "Object deleted!"},
            status=status.HTTP_200_OK
        )
