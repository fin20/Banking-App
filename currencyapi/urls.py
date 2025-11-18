from django.urls import path
from .views import CurrencyAPIView

urlpatterns = [
    path('conversion/<str:currency1>/<str:currency2>/<str:amount_of_currency1>'
         , CurrencyAPIView.as_view(), name='currency-conversion'),
]

