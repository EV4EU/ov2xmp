from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm


def forgot_password(request):
    context = {}
    return render(request, 'users/password-reset.html', context)


@login_required
def manage_users(request):
    if request.user.is_superuser:
        return render(request, 'users/manage-users.html', {'title': 'Users'})
    else:
        raise PermissionDenied


@login_required
def create_user(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            form = UserRegisterForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                messages.success(request, f'Account created for {username}')
                return redirect('home')
        else:
            form = UserRegisterForm()
        title = "Create New User"
        return render(request, 'users/create-user.html', {'form': form, 'title': title})
    else:
        raise PermissionDenied


@login_required
def get_users(request):
    response = {"data": []}
    for user in User.objects.all():
        response['data'].append({
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'superuser': user.is_superuser,
            'email': user.email,
        })
    return JsonResponse(response, safe=False)


@login_required
def delete_user(request):
    if request.user.is_superuser:
        global user
        splitted_url = request.get_full_path().split('/')
        if len(splitted_url) > 3:
            username = splitted_url[3]
            if username != '':
                user = User.objects.get(username=username)
            else:
                return HttpResponse(status=400)
        else:
            return HttpResponse(status=400)

        user.delete()
        return render(request, 'users/manage-users.html', {'title': 'Users'})
    else:
        raise PermissionDenied


@login_required
def edit_user(request):
    
    splitted_url = request.get_full_path().split('/')
    if len(splitted_url) > 3:           # Determine if a user has been specified in the URL
        username = splitted_url[3]      
        if username != '':
            edited_user = User.objects.get(username=username)  # If yes, then we are going to change their attributes
        else:
            edited_user = request.user  # if no user is specified, then we take the signed in user
            username = request.user.username
    else:
        edited_user = request.user
        username = request.user.username
    # if the logged-in user has specified a user in the URL, but they do not have the appropriate rights, raise error
    if request.user.username != edited_user.username and not request.user.is_superuser:
        raise PermissionDenied

    if request.method == 'POST':        
        # Update profile
        if 'password' not in request.POST:
            u_form = UserUpdateForm(request.POST, instance=edited_user)
            p_form = ProfileUpdateForm(request.POST,
                                       request.FILES,
                                       instance=edited_user.profile)
            if u_form.is_valid() and p_form.is_valid():
                u_form.save()
                p_form.save()
                if username != request.user.username:
                    messages.success(request, f'The account ' + username + ' has been updated')
                    return redirect('users-manage')
                else:
                    messages.success(request, f'Your account has been updated')
                    return redirect('users-edit')
            else:
                raise PermissionDenied
        
        # Update password
        else:
            pass_form = PasswordChangeForm(edited_user, request.POST)
            if pass_form.is_valid():
                pass_form.save()
            if username != request.user.username:
                messages.success(request, f'The password for user ' + username + ' has been updated')
                return redirect('users-manage')
            else:
                messages.success(request, f'Your password has been updated')
                return redirect('users-edit')
    else:
        u_form = UserUpdateForm(instance=edited_user)
        p_form = ProfileUpdateForm(instance=edited_user.profile)
        pass_form = PasswordChangeForm(edited_user)

        title = 'Profile Info'

        context = {
            'u_form': u_form,
            'p_form': p_form,
            'pass_form': pass_form,
            'title': title,
            'custom_user': edited_user
        }

        return render(request, 'users/edit-user.html', context)
