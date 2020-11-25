from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .forms import EditProfileForm, PasswordChangeForms

def signin(request):
    return redirect(reverse('Home'))

@login_required
def view_profile(request):
    if request.method=='POST':
        form = EditProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            messages.success(request, "Your <strong>Profile</strong> has been update successfully !")
            form.save()
            return redirect('/account/profile')
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
            return redirect(reverse('change_password'))
        
        else: messages.error(request, "Please correct the errors mentioned below!") 
    
    else:
        form = PasswordChangeForms(user=request.user)
    return render(request, 'accounts/password-change.html', {'form': form})
