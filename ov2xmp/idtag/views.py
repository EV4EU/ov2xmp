from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import IdTagForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from idtag.models import IdTag


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
def get_idTags(request):
    response = {"data": []}
    for _idtag in IdTag.objects.all():
        if _idtag.user is not None:
            response['data'].append({
                'idToken': _idtag.idToken,
                'expiry_date': _idtag.expiry_date,
                'revoked': _idtag.revoked,
                'username': _idtag.user.username,
            })
        else:
            response['data'].append({
                'idToken': _idtag.idToken,
                'expiry_date': _idtag.expiry_date,
                'revoked': _idtag.revoked,
                'username': None,
            })

    return JsonResponse(response, safe=False)


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
