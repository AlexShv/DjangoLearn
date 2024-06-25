from .models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import Form, CharField, TextInput, PasswordInput


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
            'password1',
            'password2',
        )


class LoginForm(Form):
    email = CharField(max_length=60, widget=TextInput())
    password = CharField(max_length=65, widget=PasswordInput())
