from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .models import Location
from .serializers import LocationSerializer
from drf_spectacular.openapi import AutoSchema


class LocationApiView(GenericAPIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LocationSerializer
    queryset = Location.objects.all()
    schema = AutoSchema()

    # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        List all the Locations
        '''
        Locations = Location.objects.all()
        serializer = LocationSerializer(Locations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request, *args, **kwargs):
        '''
        Create the Location with given data.
        '''
        print(request.data)

        data = {
            'country': request.data.get('country'), 
            'postal_code': request.data.get('postal_code'),
            'street_address': request.data.get('street_address'), 
            'city': request.data.get('city'),
            'name': request.data.get('name'),
        }

        serializer = LocationSerializer(data=data) # type: ignore
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LocationDetailApiView(GenericAPIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LocationSerializer
    schema = AutoSchema()

    def get_object(self, location_id):        
        # Helper method to get the object with given todo_id, and user_id

        try:
            return Location.objects.get(pk=location_id)
        except Location.DoesNotExist:
            return None

    # 3. Retrieve
    def get(self, request, location_id, *args, **kwargs):
        '''
        Retrieves the Location with the given ID
        '''
        location_instance = self.get_object(location_id)
        if not location_instance:
            return Response(
                {"status": "Location with the given ID does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = LocationSerializer(location_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 4. Update
    def put(self, request, location_id, *args, **kwargs):
        '''
        Updates the Location item with given id, if exists.
        '''
        location_instance = self.get_object(location_id)
        if not location_instance:
            return Response(
                {"status": "Location with the given ID does not exist"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = {
            'country': request.data.get('country'), 
            'postal_code': request.data.get('postal_code'),
            'street_address': request.data.get('street_address'), 
            'city': request.data.get('city'),
            'name': request.data.get('name'),
        }
        serializer = LocationSerializer(instance=location_instance, data=data, partial=True) # type: ignore
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 5. Delete
    def delete(self, request, location_id, *args, **kwargs):
        '''
        Deletes the Location item with given id, if exists
        '''
        location_instance = self.get_object(location_id)
        if not location_instance:
            return Response(
                {"status": "Location with the given ID does not exist"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        location_instance.delete()
        return Response(
            {"status": "Location successfully deleted"}, 
            status=status.HTTP_200_OK
        )
