from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Customer


class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(label='Username', widget=forms.TextInput(), max_length=15)
    first_name = forms.CharField(max_length=20, required=True)
    last_name = forms.CharField(max_length=20, required=True)
    email = forms.EmailField(required=True)
    currency = forms.ChoiceField(choices=Customer.CURRENCY_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'currency']
