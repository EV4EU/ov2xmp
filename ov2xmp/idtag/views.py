from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import IdTagForm
from django.contrib.auth.decorators import login_required
from idtag.models import IdTag
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .models import IdTag
from .serializers import IdTagSerializer
from rest_framework.schemas.openapi import AutoSchema


@login_required
def manage_idTags(request):
    return render(request, 'idtag/idtag-manage.html', {'title': 'ID Tags'})
    

@login_required
def add_idTag(request):
    if request.method == 'POST':
        form = IdTagForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('user')
            idToken = form.cleaned_data.get('idToken')
            if user is None:
                messages.success(request, f'ID tag "{idToken}" created')
            else:
                messages.success(request, f'ID tag "{idToken}" created for user "{user.username}"')
            return redirect('idtag-manage')
    else:
        form = IdTagForm()
    title = "Create New ID Tag"
    return render(request, 'idtag/idtag-add.html', {'form': form, 'title': title})


@login_required
def delete_idTag(request):
    splitted_url = request.get_full_path().split('/')
    if len(splitted_url) > 3:
        idtoken = splitted_url[3]
        if idtoken != '':
            idTag = IdTag.objects.get(idToken=idtoken)
        else:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=400)
    deleted_token = idTag.idToken
    idTag.delete()
    messages.success(request, f'ID tag "{deleted_token}" successfully deleted')
    return redirect('idtag-manage')


@login_required
def edit_idTag(request):
    
    splitted_url = request.get_full_path().split('/')
    if len(splitted_url) > 3:
        idtoken = splitted_url[3]      
        if idtoken != '':
            edited_idtag = IdTag.objects.get(idToken=idtoken)
        else:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=400)

    if request.method == 'POST':        
        # Update idTag
        idtag_form = IdTagForm(request.POST, instance=edited_idtag)
        if idtag_form.is_valid():
            idtag_form.save()
            messages.success(request, f'The ID Tag "{edited_idtag.idToken}" has been updated')
            return redirect('idtag-manage')
        else:
            messages.error(request, f'The ID Tag could not be updated. Please try again')
            return redirect('idtag-manage')        
    else:
        # Load form to update the IdTag
        idtag_form = IdTagForm(instance=edited_idtag)

        title = 'Update ID Tag'

        context = {
            'idtag_form': idtag_form,
            'title': title,
        }

        return render(request, 'idtag/idtag-edit.html', context)


class IdtagApiView(GenericAPIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = IdTagSerializer
    queryset = IdTag.objects.all()
    schema = AutoSchema(tags=['ID Tags'])

    # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        List all the ID Tags
        '''
        idtags = IdTag.objects.all()
        serializer = IdTagSerializer(idtags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request, *args, **kwargs):
        '''
        Create the ID Tag with given data
        '''

        serializer = IdTagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IdtagDetailApiView(GenericAPIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = IdTagSerializer
    schema = AutoSchema(tags=['ID Tags'])

    def get_object(self, id_token):        
        try:
            return IdTag.objects.get(pk=id_token)
        except IdTag.DoesNotExist:
            return None

    # 3. Retrieve
    def get(self, request, id_token, *args, **kwargs):
        '''
        Retrieves the Chargepoint with given chargepoint_url_identity
        '''
        idtag_instance = self.get_object(id_token=id_token)
        if not idtag_instance:
            return Response(
                {"res": "Object with todo id does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = IdTagSerializer(idtag_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 4. Update
    def put(self, request, id_token, *args, **kwargs):
        '''
        Updates the Chargepoint item with given chargepoint_url_identity, if exists
        '''
        idtag_instance = self.get_object(id_token)
        if not idtag_instance:
            return Response(
                {"res": "Object with todo id does not exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = IdTagSerializer(instance=idtag_instance, data=request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 5. Delete
    def delete(self, request, id_token, *args, **kwargs):
        '''
        Deletes the Chargepoint item with given chargepoint_url_identity, if exists
        '''
        idtag_instance = self.get_object(id_token)
        if not idtag_instance:
            return Response(
                {"res": "Object with todo id does not exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        idtag_instance.delete()
        return Response(
            {"res": "Object deleted!"},
            status=status.HTTP_200_OK
        )
