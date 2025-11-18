from django.shortcuts import render

# Create your views here.
from decimal import Decimal, InvalidOperation
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView


class CurrencyAPIView(APIView):

    # currency exchange rates
    CONVERSION_RATES = {
        'GBP': {'GBP': Decimal('1.0'), 'USD': Decimal('1.30'), 'EUR': Decimal('1.17')},
        'USD': {'GBP': Decimal('0.77'), 'USD': Decimal('1.0'), 'EUR': Decimal('0.90')},
        'EUR': {'GBP': Decimal('0.85'), 'USD': Decimal('1.11'), 'EUR': Decimal('1.0')}
    }

    def get(self, request, currency1, currency2, amount_of_currency1):
        try:
            amount = Decimal(amount_of_currency1)
            rate = self.CONVERSION_RATES[currency1][currency2]
            converted_amount = amount * rate
            return Response({
                "from": currency1,
                "to": currency2,
                "rate": str(rate.quantize(Decimal('0.0001'))),
                "converted_amount": str(converted_amount.quantize(Decimal('0.01')))  # 2dp
            })
        except (ValueError, InvalidOperation):
            return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({"error": "Invalid currency"}, status=status.HTTP_400_BAD_REQUEST)
