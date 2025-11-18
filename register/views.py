from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User, Group
import requests
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect

from .forms import UserRegistrationForm
from django.contrib.auth import authenticate, login as auth_login
from .models import Customer


# currency conversion api call
def convert_currency(request, from_currency, to_currency, amount):
    try:
        base_url = "https://127.0.0.1:8000"
        api_url = f"{base_url}/currencyapi/conversion/{from_currency}/{to_currency}/{amount}"
        response = requests.get(api_url, verify=False)

        if response.status_code == 200:
            data = response.json()
            return Decimal(str(data['converted_amount']))
        else:
            messages.error(request, "Error in converting currencies.")
            raise ValueError("Currency conversion failed")
    except Exception as e:
        messages.error(request, f'Error: {e}')
        raise ValueError("Currency conversion failed")


@csrf_protect
def register_customer(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data['username']).exists():
                messages.error(request, 'Username already exists')
                return redirect('register-customer')
            elif User.objects.filter(email=form.cleaned_data['email']).exists():
                messages.error(request, 'Email already exists')
                return redirect('register-customer')

            user = form.save()
            customers_group = Group.objects.get(name='Customers')
            customers_group.user_set.add(user)

            default_balance_gbp = 750.00
            selected_currency = form.cleaned_data['currency']

            try:
                if selected_currency != 'GBP':
                    adjusted_balance = convert_currency(
                        request,
                        'GBP',
                        selected_currency,
                        default_balance_gbp
                    )
                else:
                    adjusted_balance = Decimal(default_balance_gbp)

                Customer.objects.create(user=user, currency=form.cleaned_data['currency'], balance=adjusted_balance)
                messages.success(request, 'Your account has been created!')
                return redirect('login-user')

            except ValueError:
                user.delete()
                return redirect('register-customer')
    else:
        form = UserRegistrationForm()
    return render(request, 'register/register.html', {"form": form})


@csrf_protect
def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth_login(request, user)
                if user.groups.filter(name='Admins').exists():
                    return redirect('admin-home')
                elif user.groups.filter(name='Customers').exists():
                    return redirect('customer-home')
        else:
            messages.error(request, 'Invalid username or password. Try again.')
            return redirect('login-user')
    else:
        form = AuthenticationForm()
    return render(request, 'register/login.html', {"form": form})
