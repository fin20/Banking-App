from decimal import Decimal
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from register.models import Customer, Transaction, Request
from .forms import TransferMoneyForm, RequestMoneyForm
from django.views.decorators.csrf import csrf_protect


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
            messages.error(request, "Error in converting amount.")
            return redirect("transfer-payment")
    except Exception as e:
        messages.error(request, f'Error during transfer: {e}')
        return redirect('transfer-payment')


@csrf_protect
@login_required
def transfer_payment(request):
    if request.method == 'POST':
        form = TransferMoneyForm(request.POST)
        if form.is_valid():
            recipient_username = form.cleaned_data['username']
            amount = form.cleaned_data['amount']

            try:
                sender_account = Customer.objects.get(user=request.user)
                recipient_account = Customer.objects.get(user__username=recipient_username)

                # checks
                if sender_account.user == recipient_account.user:
                    messages.error(request, 'You cannot transfer money to yourself')
                    return redirect('transfer-payment')

                if sender_account.balance < amount:
                    messages.error(request, 'Insufficient funds')
                    return redirect('transfer-payment')

                if amount < 0:
                    messages.error(request, 'Amount must be positive')
                    return redirect('transfer-payment')

                # old hard coded currency conversions
                # rates = {'GBP': Decimal('1.0'), 'USD': Decimal('1.30'), 'EUR': Decimal('1.17')}

                with transaction.atomic():
                    # if sender_account.currency != recipient_account.currency:
                    #     gbp_amount = amount / rates[sender_account.currency]
                    #     convert_amount = gbp_amount * rates[recipient_account.currency]
                    # else:
                    #     convert_amount = amount
                    if sender_account.currency != recipient_account.currency:
                        convert_amount = convert_currency(
                            request,
                            sender_account.currency,
                            recipient_account.currency,
                            amount
                        )
                    else:
                        convert_amount = amount

                    sender_account.balance -= Decimal(amount)
                    sender_account.save()

                    recipient_account.balance += Decimal(convert_amount)
                    recipient_account.save()

                    # log transaction for sender
                    Transaction.objects.create(
                        account=sender_account,
                        amount=f"-{amount} {sender_account.currency}",
                        transaction_type="payment",
                        description=f"Payment to {recipient_username}"
                    )

                    # log transaction for recipient
                    Transaction.objects.create(
                        account=recipient_account,
                        amount=f"+{convert_amount} {recipient_account.currency}",
                        transaction_type="payment",
                        description=f"Payment from {request.user.username}"
                    )

                    # confirmations and error exceptions
                    if sender_account.currency != recipient_account.currency:
                        messages.success(request,
                                         f"Successfully transferred {amount} {sender_account.currency} "
                                         f"({convert_amount:.2f} {recipient_account.currency}) to {recipient_username}.")
                    else:
                        messages.success(request,
                                         f"Successfully transferred {amount} {sender_account.currency} to {recipient_username}.")
                    return redirect('customer-home')

            except Customer.DoesNotExist:
                messages.error(request, 'Recipient not found')
                return redirect('transfer-payment')
            except Exception as e:
                messages.error(request, f'Error during transfer: {e}')
                return redirect('transfer-payment')
        else:
            messages.error(request, 'Invalid data')
            return redirect('transfer-payment')
    else:
        form = TransferMoneyForm()
        sender_account = Customer.objects.get(user=request.user)

    return render(request, 'customer/transfer-payment.html', {'form': form, 'account': sender_account})


@csrf_protect
@login_required
def response_payment(request):
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        response_action = request.POST.get('response')

        payment_request = get_object_or_404(
            Request,
            id=request_id,
            sender__user=request.user,
            is_accepted=False
        )

        try:
            if response_action == 'Accept':
                recipient_account = payment_request.sender  # request recipient/payment sender
                sender_account = payment_request.recipient  # request sender/payment receiver
                amount = payment_request.amount

                if recipient_account.balance < amount:
                    messages.error(request, 'Insufficient funds to fulfill request')
                    return redirect('manage-requests')

                # old hard coded currency conversions
                # rates = {'GBP': Decimal('1.0'), 'USD': Decimal('1.30'), 'EUR': Decimal('1.17')}

                with transaction.atomic():
                    recipient_account.balance -= Decimal(amount)
                    recipient_account.save()

                    # if recipient_account.currency != sender_account.currency:
                    #     gbp_amount = amount / rates[recipient_account.currency]
                    #     convert_amount = gbp_amount * rates[sender_account.currency]
                    # else:
                    #     convert_amount = amount

                    if recipient_account.currency != sender_account.currency:
                        convert_amount = convert_currency(
                            request,
                            recipient_account.currency,
                            sender_account.currency,
                            amount
                        )
                    else:
                        convert_amount = amount

                    sender_account.balance += Decimal(convert_amount)
                    sender_account.save()

                    # log transaction for request recipient/payment sender
                    Transaction.objects.create(
                        account=recipient_account,
                        amount=f"-{amount} {recipient_account.currency}",
                        transaction_type='payment',
                        description=f"Payment to {sender_account.user.username} accepted"
                    )

                    # log transaction for request sender/payment receiver
                    Transaction.objects.create(
                        account=sender_account,
                        amount=f"+{convert_amount} {sender_account.currency}",
                        transaction_type='payment',
                        description=f"Payment from {recipient_account.user.username} accepted"
                    )

                    payment_request.is_accepted = True
                    payment_request.date_responded = timezone.now()
                    payment_request.save()

                    # confirmation checks and error exceptions
                    if recipient_account.currency != sender_account.currency:
                        messages.success(request,
                                         f"Payment request accepted. {amount} {recipient_account.currency} "
                                         f"({convert_amount:.2f} {sender_account.currency}) sent to {sender_account.user.username}.")
                    else:
                        messages.success(request,
                                         f"Payment request accepted. {amount} {recipient_account.currency} sent to {sender_account.user.username}.")

            elif response_action == 'Reject':
                payment_request.is_accepted = False
                payment_request.date_responded = timezone.now()
                payment_request.save()
                messages.info(request, "Payment request rejected.")
                return redirect('manage-requests')

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('manage-requests')

    pending_requests = Request.objects.filter(
        sender=request.user.account,
        is_accepted=False,
        date_responded__isnull=True
    )

    return render(request, 'customer/customer-requests.html', {'pending_requests': pending_requests})


@csrf_protect
@login_required
def request_payment(request):
    if request.method == 'POST':
        form = RequestMoneyForm(request.POST)
        if form.is_valid():
            recipient_username = form.cleaned_data['username']
            amount = form.cleaned_data['amount']

            try:
                recipient_account = Customer.objects.get(user__username=recipient_username)  # user who receives the request
                requester_account = Customer.objects.get(user=request.user)  # user who requested the payment

                # checks
                if requester_account.user == recipient_account.user:
                    messages.error(request, 'You cannot transfer money to yourself')
                    return redirect('request-payment')

                if amount < 0:
                    messages.error(request, 'Amount must be positive')
                    return redirect('request-payment')

                # old hard coded currency conversions
                # rates = {'GBP': Decimal('1.0'), 'USD': Decimal('1.30'), 'EUR': Decimal('1.17')}
                #
                # if requester_account.currency != recipient_account.currency:
                #     gbp_amount = amount / rates[requester_account.currency]
                #     convert_amount = gbp_amount * rates[recipient_account.currency]
                # else:
                #     convert_amount = amount

                if requester_account.currency != recipient_account.currency:
                    convert_amount = convert_currency(
                        request,
                        requester_account.currency,
                        recipient_account.currency,
                        amount
                    )
                else:
                    convert_amount = amount

                Request.objects.create(
                    sender=recipient_account,
                    recipient=requester_account,
                    amount=convert_amount,
                    description=f"Request for {amount} {requester_account.currency}",
                    is_accepted=False
                )
                # confirmations and error handling
                messages.success(request,
                                 f"Payment request of {amount} {requester_account.currency} sent to {recipient_account.user.username}.")
                return redirect('customer-home')
            except Customer.DoesNotExist:
                messages.error(request, 'Recipient not found')
            except Exception as e:
                messages.error(request, f'Error during request: {e}')
        else:
            messages.error(request, 'Invalid form data')
            return redirect('request-payment')
    else:
        form = RequestMoneyForm()
    return render(request, 'customer/request-payment.html', {'form': form})
