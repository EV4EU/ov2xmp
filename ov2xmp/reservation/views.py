from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .models import Reservation
from .serializers import ReservationSerializer
from drf_spectacular.openapi import AutoSchema


class ReservationApiView(GenericAPIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReservationSerializer
    queryset = Reservation.objects.all()
    schema = AutoSchema()

    # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        List all the Reservations
        '''
        Reservations = Reservation.objects.all()
        serializer = ReservationSerializer(Reservations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request, *args, **kwargs):
        '''
        Create the Reservation with given data. 
        '''

        serializer = ReservationSerializer(data=request.data) # type: ignore
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReservationDetailApiView(GenericAPIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReservationSerializer
    schema = AutoSchema()

    def get_object(self, Reservation_id):        
        # Helper method to get the object with given todo_id, and user_id

        try:
            return Reservation.objects.get(pk=Reservation_id)
        except Reservation.DoesNotExist:
            return None

    # 3. Retrieve
    def get(self, request, reservation_id, *args, **kwargs):
        '''
        Retrieves the Reservation with given ID
        '''
        reservation_instance = self.get_object(reservation_id)
        if not reservation_instance:
            return Response(
                {"status": "Reservation with the given ID does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ReservationSerializer(reservation_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 4. Update
    def put(self, request, reservation_id, *args, **kwargs):
        '''
        Updates the Reservation item with given id, if exists.
        '''
        reservation_instance = self.get_object(reservation_id)
        if not reservation_instance:
            return Response(
                {"status": "Reservation with the given ID does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ReservationSerializer(instance=reservation_instance, data=request.data, partial=True) # type: ignore
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 5. Delete
    def delete(self, request, reservation_id, *args, **kwargs):
        '''
        Deletes the Reservation item with given id, if exists
        '''
        reservation_instance = self.get_object(reservation_id)
        if not reservation_instance:
            return Response(
                {"status": "Reservation with the given ID does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
        reservation_instance.delete()
        return Response(
            {"status": "Reservation deleted!"},
            status=status.HTTP_200_OK
        )
