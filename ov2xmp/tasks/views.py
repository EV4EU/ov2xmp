from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from django_celery_results.models import TaskResult
from .serializers import TaskResultSerializer
from drf_spectacular.openapi import AutoSchema


# Create your views here.
class TasksApiView(GenericAPIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskResultSerializer
    queryset = TaskResult.objects.all()
    schema = AutoSchema()

    # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        List all Tasks
        '''
        chargepoints = TaskResult.objects.all()
        serializer = TaskResultSerializer(chargepoints, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TasksDetailApiView(GenericAPIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskResultSerializer
    schema = AutoSchema()

    def get_object(self, task_id):        
        # Helper method to get the object with given todo_id, and user_id

        try:
            return TaskResult.objects.get(task_id=task_id)
        except TaskResult.DoesNotExist:
            return None

    # 3. Retrieve
    def get(self, request, task_id, *args, **kwargs):
        '''
        Retrieves the Chargepoint with given chargepoint_id
        '''
        task_instance = self.get_object(task_id=task_id)
        if not task_instance:
            return Response(
                {"status": "Task does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = TaskResultSerializer(task_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


    # 5. Delete
    def delete(self, request, task_id, *args, **kwargs):
        '''
        Deletes the Chargepoint item with given chargepoint_id, if exists
        '''
        task_instance = self.get_object(task_id)
        if not task_instance:
            return Response(
                {"status": "Task does not exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        task_instance.delete()
        return Response(
            {"status": "Task deleted!"},
            status=status.HTTP_200_OK
        )
