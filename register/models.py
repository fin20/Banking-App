from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class Customer(models.Model):
    CURRENCY_CHOICES = [
        ('GBP', 'GB Pounds'),
        ('USD', 'US Dollars'),
        ('EUR', 'Euros'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account')
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='GBP')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username}'s Account)"


# transaction log
class Transaction(models.Model):
    account = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='transactions')
    date = models.DateTimeField(auto_now_add=True)
    amount = models.CharField(max_length=10)
    transaction_type = models.CharField(max_length=50)  # e.g., "deposit", "withdrawal", "payment"
    description = models.TextField()


# money requests
class Request(models.Model):
    sender = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='sent_requests')
    recipient = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='received_requests')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(max_length=255, blank=True)
    is_accepted = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_responded = models.DateTimeField(null=True, blank=True)


# create admin user
class Admins(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} Admin Profile"
