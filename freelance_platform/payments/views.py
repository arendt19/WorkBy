from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db import transaction as db_transaction
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta
from django.utils.translation import get_language

from .models import Transaction, Wallet, WithdrawalMethod, WithdrawalRequest
from .forms import DepositForm, WithdrawForm, TransactionFilterForm, WithdrawalForm, TopUpForm, PaymentMethodForm
from jobs.models import Milestone, Contract
from .yoomoney import YooMoneyAPI

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
    
    try:
        # Используем класс для работы с API ЮMoney
        yoomoney_api = YooMoneyAPI()
        
        # Метаданные для платежа
        metadata = {'milestone_id': milestone_id} if milestone_id else None
        
        # Создаем платеж
        payment_info = yoomoney_api.create_payment(
            amount=amount,
            return_url=request.build_absolute_uri(reverse('payments:yoomoney_success_callback')),
            description=_("Payment to WorkBy"),
            metadata=metadata
        )
        
        # Перенаправляем на страницу оплаты
        return redirect(payment_info['confirmation']['confirmation_url'])
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_GET
def yoomoney_success_callback(request):
    """
    Обработчик успешного платежа через ЮMoney
    """
    payment_id = request.GET.get('payment_id')
    
    if not payment_id:
        messages.error(request, _("Invalid payment ID"))
        return redirect('payments:wallet')
    
    try:
        # Используем класс для работы с API ЮMoney
        yoomoney_api = YooMoneyAPI()
        
        # Получаем информацию о платеже
        payment_info = yoomoney_api.get_payment_status(payment_id)
        
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
                return redirect('jobs:contract_detail', pk=contract.pk)
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
    except Exception as e:
        messages.error(request, _(f"Error processing payment: {str(e)}"))
        return redirect('payments:wallet')

@csrf_exempt
@require_POST
def yoomoney_notification_callback(request):
    """
    Обработчик уведомлений от ЮMoney
    """
    try:
        # Проверяем подпись уведомления
        signature = request.headers.get('X-Payment-Sha1-Hash')
        
        # Используем класс для работы с API ЮMoney
        yoomoney_api = YooMoneyAPI()
        
        # Проверяем подпись
        if not yoomoney_api.verify_notification(request.body.decode(), signature):
            return HttpResponse(status=400)
        
        # Обрабатываем уведомление
        notification = json.loads(request.body)
        
        if notification['event'] == 'payment.succeeded':
            payment_id = notification['object']['id']
            
            # Получаем информацию о платеже
            payment_info = yoomoney_api.get_payment_status(payment_id)
            
            if payment_info['status'] == 'succeeded':
                # Получаем данные из метаданных
                metadata = payment_info.get('metadata', {})
                milestone_id = metadata.get('milestone_id')
                user_id = metadata.get('user_id')
                
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
                elif user_id:
                    # Если это пополнение кошелька
                    from accounts.models import User
                    user = get_object_or_404(User, id=user_id)
                    amount = payment_info['amount']['value']
                    
                    with db_transaction.atomic():
                        wallet, _ = Wallet.objects.get_or_create(user=user)
                        wallet.deposit(
                            amount=amount,
                            description=_("Deposit via YooMoney")
                        )
        
        return HttpResponse(status=200)
    except Exception as e:
        # Логирование ошибки
        print(f"Error processing YooMoney notification: {str(e)}")
        return HttpResponse(status=500) 