from django.contrib.auth.forms import (PasswordChangeForm, UserChangeForm)
from django.contrib.auth.models import User

class EditProfileForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["placeholder"] = "Username"
        self.fields["username"].widget.attrs["class"] = "form-control mb-20"
        self.fields['username'].label = "Your Username"

        self.fields["email"].widget.attrs["placeholder"] = "Email address"
        self.fields["email"].widget.attrs["class"] = "form-control mb-20"
        self.fields['email'].label = "Your account email address"

        self.fields["first_name"].widget.attrs["placeholder"] = "First Name"
        self.fields["first_name"].widget.attrs["class"] = "form-control mb-20"

        self.fields["last_name"].widget.attrs["placeholder"] = "Last Name"
        self.fields["last_name"].widget.attrs["class"] = "form-control mb-20"

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',      
        )

class PasswordChangeForms(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields["old_password"].widget.attrs["placeholder"] = "Current Password"
        self.fields["old_password"].widget.attrs["class"] = "form-control mb-20"
        self.fields['old_password'].label = "Current Password"

        self.fields["new_password1"].widget.attrs["placeholder"] = "New Password"
        self.fields["new_password1"].widget.attrs["class"] = "form-control mb-10 "

        self.fields["new_password2"].widget.attrs["placeholder"] = "Retype the new password"
        self.fields["new_password2"].widget.attrs["class"] = "form-control mb-10 "
