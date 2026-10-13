from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class StudentRegisterForm(UserCreationForm):
    """
    Form for self-registration of students.
    Automatically assigns role='student'.
    """
    email = forms.EmailField(
        required=True,
        help_text="Required for placement updates and notifications"
    )
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def save(self, commit=True):
        # Force the role to 'student' upon self-registration
        user = super().save(commit=False)
        user.role = 'student'
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    """
    Standard login form utilizing Django's built-in authentication.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter username', 'autofocus': True})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'})
    )
