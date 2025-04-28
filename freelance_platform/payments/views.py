from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db import transaction as db_transaction
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta
from django.utils.translation import get_language

from .models import Transaction, Wallet
from .forms import DepositForm, WithdrawForm, TransactionFilterForm
from jobs.models import Milestone

# ЮMoney интеграция
import json
import hmac
import hashlib
import requests
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.urls import reverse
import uuid

@login_required
def wallet_view(request):
    """
    Страница кошелька пользователя
    """
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    # Получаем последние транзакции
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Статистика
    stats = {
        'total_earned': Transaction.objects.filter(
            user=request.user,
            transaction_type='deposit',
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0,
        
        'total_spent': Transaction.objects.filter(
            user=request.user,
            transaction_type__in=['withdrawal', 'payment', 'fee'],
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0,
    }
    
    # Статистика по месяцам
    now = timezone.now()
    month_ago = now - timedelta(days=30)
    
    monthly_stats = {
        'month_earned': Transaction.objects.filter(
            user=request.user,
            transaction_type='deposit',
            status='completed',
            created_at__gte=month_ago
        ).aggregate(total=Sum('amount'))['total'] or 0,
        
        'month_spent': Transaction.objects.filter(
            user=request.user,
            transaction_type__in=['withdrawal', 'payment', 'fee'],
            status='completed',
            created_at__gte=month_ago
        ).aggregate(total=Sum('amount'))['total'] or 0,
    }
    
    # Статистика по типам транзакций
    type_stats = {}
    for t_type, _ in Transaction.TRANSACTION_TYPES:
        type_stats[t_type] = Transaction.objects.filter(
            user=request.user,
            transaction_type=t_type,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'wallet': wallet,
        'transactions': transactions,
        'stats': stats,
        'monthly_stats': monthly_stats,
        'type_stats': type_stats,
    }
    
    return render(request, 'payments/wallet.html', context)

@login_required
def transaction_list_view(request):
    """
    Страница со списком всех транзакций
    """
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    # Базовый QuerySet
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    
    # Фильтрация транзакций
    form = TransactionFilterForm(request.GET)
    if form.is_valid():
        # Фильтр по типу
        if form.cleaned_data.get('type'):
            transactions = transactions.filter(transaction_type=form.cleaned_data['type'])
        
        # Фильтр по статусу
        if form.cleaned_data.get('status'):
            transactions = transactions.filter(status=form.cleaned_data['status'])
        
        # Фильтр по датам
        if form.cleaned_data.get('date_from'):
            transactions = transactions.filter(created_at__date__gte=form.cleaned_data['date_from'])
        
        if form.cleaned_data.get('date_to'):
            transactions = transactions.filter(created_at__date__lte=form.cleaned_data['date_to'])
    
    context = {
        'wallet': wallet,
        'transactions': transactions,
        'form': form,
    }
    
    return render(request, 'payments/transaction_list.html', context)

@login_required
def transaction_detail_view(request, transaction_id):
    """
    Страница с детальной информацией о транзакции
    """
    transaction = get_object_or_404(Transaction, transaction_id=transaction_id, user=request.user)
    
    context = {
        'transaction': transaction,
    }
    
    return render(request, 'payments/transaction_detail.html', context)

@login_required
def deposit_view(request):
    """
    Страница для пополнения кошелька через ЮMoney
    """
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            
            # Инициируем платеж через ЮMoney
            payment_url = reverse('payments:yoomoney_initiate_payment')
            return redirect(f"{payment_url}?amount={amount}")
    else:
        form = DepositForm()
    
    context = {
        'wallet': wallet,
        'form': form,
    }
    
    return render(request, 'payments/deposit.html', context)

@login_required
def withdraw_view(request):
    """
    Страница для вывода средств через ЮMoney
    """
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = WithdrawForm(request.POST, user=request.user)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            
            try:
                with db_transaction.atomic():
                    description = _("Withdrawal to YooMoney")
                    wallet.withdraw(amount, description=description)
                
                messages.success(request, _("Your withdrawal request has been processed"))
                return redirect('payments:wallet')
                
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = WithdrawForm(user=request.user)
    
    context = {
        'wallet': wallet,
        'form': form,
    }
    
    return render(request, 'payments/withdraw.html', context)

@login_required
def pay_milestone_view(request, milestone_id):
    """
    Страница для оплаты вехи через ЮMoney
    """
    milestone = get_object_or_404(Milestone, id=milestone_id)
    contract = milestone.contract
    
    # Проверяем, что пользователь является клиентом по контракту
    if request.user != contract.client:
        messages.error(request, _("You are not authorized to pay for this milestone"))
        return redirect('jobs:contract_detail', contract_id=contract.id)
    
    # Проверяем, что веха еще не оплачена
    if milestone.is_paid:
        messages.error(request, _("This milestone has already been paid"))
        return redirect('jobs:contract_detail', contract_id=contract.id)
    
    if request.method == 'POST':
        amount = milestone.amount
        
        # Инициируем платеж через ЮMoney
        payment_url = reverse('payments:yoomoney_initiate_payment')
        return redirect(f"{payment_url}?amount={amount}&milestone_id={milestone.id}")
    
    context = {
        'milestone': milestone,
        'contract': contract,
    }
    
    return render(request, 'payments/pay_milestone.html', context)

def yoomoney_initiate_payment(request):
    """
    Инициирует платеж через ЮMoney
    """
    amount = request.GET.get('amount')
    milestone_id = request.GET.get('milestone_id')
    
    if not amount:
        return JsonResponse({'error': 'Amount is required'}, status=400)
    
    # Создаем уникальный идентификатор платежа
    payment_id = str(uuid.uuid4())
    
    # Формируем данные для запроса к API ЮMoney
    payment_data = {
        'amount': {
            'value': str(amount),
            'currency': 'KZT'
        },
        'confirmation': {
            'type': 'redirect',
            'return_url': request.build_absolute_uri(reverse('payments:yoomoney_success_callback'))
        },
        'capture': True,
        'description': f'Payment {payment_id}',
        'metadata': {
            'payment_id': payment_id,
            'milestone_id': milestone_id
        }
    }
    
    # Отправляем запрос к API ЮMoney
    headers = {
        'Authorization': f'Bearer {settings.YOOMONEY_SETTINGS["CLIENT_SECRET"]}',
        'Content-Type': 'application/json'
    }
    
    response = requests.post(
        'https://api.yoomoney.ru/v3/payments',
        headers=headers,
        json=payment_data
    )
    
    if response.status_code == 200:
        payment_info = response.json()
        return redirect(payment_info['confirmation']['confirmation_url'])
    else:
        return JsonResponse({'error': 'Failed to initiate payment'}, status=400)

@require_GET
def yoomoney_success_callback(request):
    """
    Обработчик успешного платежа через ЮMoney
    """
    payment_id = request.GET.get('payment_id')
    
    if not payment_id:
        messages.error(request, _("Invalid payment ID"))
        return redirect('payments:wallet')
    
    # Проверяем статус платежа через API ЮMoney
    headers = {
        'Authorization': f'Bearer {settings.YOOMONEY_SETTINGS["CLIENT_SECRET"]}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(
        f'https://api.yoomoney.ru/v3/payments/{payment_id}',
        headers=headers
    )
    
    if response.status_code == 200:
        payment_info = response.json()
        
        if payment_info['status'] == 'succeeded':
            # Получаем данные из метаданных
            metadata = payment_info.get('metadata', {})
            milestone_id = metadata.get('milestone_id')
            
            if milestone_id:
                # Если это оплата вехи
                milestone = get_object_or_404(Milestone, id=milestone_id)
                contract = milestone.contract
                
                with db_transaction.atomic():
                    # Создаем транзакцию для клиента
                    client_wallet, _ = Wallet.objects.get_or_create(user=contract.client)
                    client_wallet.payment(
                        amount=payment_info['amount']['value'],
                        contract=contract,
                        milestone=milestone,
                        description=_("Payment for milestone")
                    )
                    
                    # Обновляем статус вехи
                    milestone.is_paid = True
                    milestone.paid_at = timezone.now()
                    milestone.save()
                
                messages.success(request, _("Milestone payment completed successfully"))
                return redirect('jobs:contract_detail', contract_id=contract.id)
            else:
                # Если это пополнение кошелька
                amount = payment_info['amount']['value']
                
                with db_transaction.atomic():
                    wallet, _ = Wallet.objects.get_or_create(user=request.user)
                    wallet.deposit(
                        amount=amount,
                        description=_("Deposit via YooMoney")
                    )
                
                messages.success(request, _("Your wallet has been successfully funded"))
                return redirect('payments:wallet')
        else:
            messages.error(request, _("Payment failed"))
            return redirect('payments:wallet')
    else:
        messages.error(request, _("Failed to verify payment status"))
        return redirect('payments:wallet')

@csrf_exempt
@require_POST
def yoomoney_notification_callback(request):
    """
    Обработчик уведомлений от ЮMoney
    """
    # Проверяем подпись уведомления
    signature = request.headers.get('X-Payment-Sha1-Hash')
    if not signature:
        return HttpResponse(status=400)
    
    # Вычисляем подпись
    expected_signature = hmac.new(
        settings.YOOMONEY_SETTINGS['CLIENT_SECRET'].encode(),
        request.body,
        hashlib.sha1
    ).hexdigest()
    
    if signature != expected_signature:
        return HttpResponse(status=400)
    
    # Обрабатываем уведомление
    notification = json.loads(request.body)
    
    if notification['event'] == 'payment.succeeded':
        payment_id = notification['object']['id']
        
        # Проверяем статус платежа через API ЮMoney
        headers = {
            'Authorization': f'Bearer {settings.YOOMONEY_SETTINGS["CLIENT_SECRET"]}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f'https://api.yoomoney.ru/v3/payments/{payment_id}',
            headers=headers
        )
        
        if response.status_code == 200:
            payment_info = response.json()
            
            if payment_info['status'] == 'succeeded':
                # Получаем данные из метаданных
                metadata = payment_info.get('metadata', {})
                milestone_id = metadata.get('milestone_id')
                
                if milestone_id:
                    # Если это оплата вехи
                    milestone = get_object_or_404(Milestone, id=milestone_id)
                    contract = milestone.contract
                    
                    with db_transaction.atomic():
                        # Создаем транзакцию для клиента
                        client_wallet, _ = Wallet.objects.get_or_create(user=contract.client)
                        client_wallet.payment(
                            amount=payment_info['amount']['value'],
                            contract=contract,
                            milestone=milestone,
                            description=_("Payment for milestone")
                        )
                        
                        # Обновляем статус вехи
                        milestone.is_paid = True
                        milestone.paid_at = timezone.now()
                        milestone.save()
                else:
                    # Если это пополнение кошелька
                    amount = payment_info['amount']['value']
                    
                    with db_transaction.atomic():
                        wallet, _ = Wallet.objects.get_or_create(user=request.user)
                        wallet.deposit(
                            amount=amount,
                            description=_("Deposit via YooMoney")
                        )
    
    return HttpResponse(status=200) 