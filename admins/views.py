from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from .forms import AdminRegistrationForm
from register.models import Customer, Transaction, Admins, Request


@csrf_protect
@login_required
def admin_view(request):
    # admin checks
    if not request.user.groups.filter(name='Admins').exists():
        messages.add_message(request, messages.ERROR, 'You do not have permission to access this page.')
        return redirect('home-page')

    # users that are not in admin group
    users = Customer.objects.select_related('user').all()
    transactions = Transaction.objects.all()
    requests = Request.objects.all()

    context = {
        'users': users,
        'transactions': transactions,
        'requests': requests
    }

    return render(request, 'home/admin-home.html', context)


@csrf_protect
@login_required
def admin_register(request):
    if not request.user.groups.filter(name='Admins').exists():
        messages.add_message(request, messages.ERROR, 'You do not have permission to access this page.')
        return redirect('home-page')

    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)

        # checks
        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data['username']).exists():
                messages.error(request, 'Username already taken.')
                return redirect('register-admin')
            if User.objects.filter(email=form.cleaned_data['email']).exists():
                messages.error(request, 'Email already taken.')
                return redirect('register-admin')

            user = form.save()

            admin_group = Group.objects.get(name='Admins')
            user.groups.add(admin_group)

            Admins.objects.create(user=user)
            messages.success(request, f'Admin account for {user.username} has been created!')
            return redirect('register-admin')
    else:
        form = AdminRegistrationForm()
    return render(request, 'register/register-admin.html', {'form': form})
