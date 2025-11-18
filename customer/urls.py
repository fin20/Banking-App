from django.urls import path
from payapp.views import *
from .views import customer_view

urlpatterns = [
    path('customer/', customer_view, name='customer-home'),
    path('transfer/', transfer_payment, name='transfer-payment'),
    path('request/', request_payment, name='request-payment'),
    path('managerequests/', response_payment, name='manage-requests'),
]
