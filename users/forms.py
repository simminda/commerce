from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User
from django import forms


class EditProfileForm(UserChangeForm):
    email = forms.EmailField(widget=forms.TextInput(
        attrs={'class': 'form-control'}), )
    first_name = forms.CharField(
        max_length=24, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(
        max_length=24, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'hidden'}), )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password')

    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'


class ChangePasswordForm(PasswordChangeForm):

    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')

    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

        self.fields['old_password'].widget.attrs['class'] = 'form-control'
        self.fields['new_password1'].widget.attrs['placeholder'] = 'Enter New Password'
        self.fields['new_password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['old_password'].label = ''
