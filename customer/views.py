# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from register.models import Customer, Transaction, Request
from django.contrib import messages


@login_required
def customer_view(request):

    # check if admin exists
    if request.user.groups.filter(name='Admins').exists():
        return redirect('admin-home')

    # get current user data
    user_account = Customer.objects.get(user=request.user)
    user_transactions = Transaction.objects.filter(account=user_account).order_by('-date')

    # pass the details to the template
    context = {
        'user': request.user,
        'account': user_account,
        'transactions': user_transactions,
    }
    return render(request, 'customer/customer-home.html', context)


@login_required
def manage_requests(request):
    try:
        # get data
        user_account = Customer.objects.get(user=request.user)
        pending_requests = Request.objects.filter(recipient=user_account, is_accepted=False)
    except Customer.DoesNotExist:
        messages.error(request, "User not found")
        pending_requests = []
    return render(request, 'customer/customer-requests.html', {'pending_requests': pending_requests})
