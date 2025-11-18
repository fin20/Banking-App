from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import Http404
from django.views.decorators.csrf import csrf_protect


@csrf_protect
def home(request):
    return render(request, 'home/home.html')


# @login_required
# def customer_home(request):
#     return render(request, 'customer/customer-home.html')
