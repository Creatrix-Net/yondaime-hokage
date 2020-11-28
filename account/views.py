from django.contrib import messages
from django.contrib.auth import (authenticate, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .forms import EditProfileForm, LoginForm, PasswordChangeForms

@login_required
def signout(request):
    logout(request)
    return redirect(reverse('Home'))


@login_required
def view_profile(request):
    if request.method=='POST':
        form = EditProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            messages.success(request, "Your <strong>Profile</strong> has been update successfully !")
            form.save()
            return redirect(reverse('Profile'))
        else: messages.error(request, "Please correct the errors mentioned below!") 
    
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def change_password(request):
    if request.method=='POST':
        form = PasswordChangeForms(data=request.POST, user=request.user)

        if form.is_valid():
            messages.success(request, "Your <strong>password</strong> has been update successfully !")
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect(reverse('Change Password'))
        
        else: messages.error(request, "Please correct the errors mentioned below!") 
    
    else:
        form = PasswordChangeForms(user=request.user)
    return render(request, 'accounts/password-change.html', {'form': form})


def signin(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in!")
        return redirect(reverse('Home'))
    else:
        if request.method == 'POST':
            form = LoginForm(request=request, data=request.POST)

            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')

                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect(reverse('discord_bind_index'))
                else: messages.error(request, "Invalid username or password.")
            else: messages.error(request, "Invalid username or password.")

        else:
            form = LoginForm()

    return render(request, 'login.html', {
        'title':'| Login |',
        'form': form, 
        'heading':'Login',
    })
