from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db import transaction as db_transaction
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta
from django.utils.translation import get_language
from decimal import Decimal

from .models import Transaction, Wallet, WithdrawalMethod, WithdrawalRequest, EscrowPayment
from .forms import DepositForm, WithdrawForm, TransactionFilterForm, TopUpForm, PaymentMethodForm
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
        'debug': settings.DEBUG,  # Передаем режим отладки
    }
    
    return render(request, 'payments/wallet.html', context)

@login_required
def demo_add_balance_view(request, amount=10000):
    """
    Демонстрационная функция для тестирования - добавляет средства на баланс пользователя
    Только для локальной разработки!
    """
    if not settings.DEBUG:
        messages.error(request, _("This feature is only available in development mode."))
        return redirect('payments:wallet')
        
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    try:
        with db_transaction.atomic():
            # Создаем демонстрационную транзакцию
            transaction_id = f"demo-{uuid.uuid4()}"
            transaction = Transaction.objects.create(
                user=request.user,
                amount=amount,
                transaction_type='deposit',
                status='completed',
                description=_("Demo balance for testing"),
                transaction_id=transaction_id,
                payment_method='demo'  # Добавляем payment_method, который требуется в БД
            )
            
            # Обновляем баланс кошелька
            wallet.balance += Decimal(amount)
            wallet.save(update_fields=['balance'])
            
            messages.success(request, _(f"Successfully added {amount} ₸ to your balance for testing."))
    except Exception as e:
        messages.error(request, str(e))
    
    return redirect('payments:wallet')

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

@login_required
def create_escrow_payment(request, milestone_id):
    """
    Создание эскроу-платежа для вехи
    """
    milestone = get_object_or_404(Milestone, id=milestone_id)
    contract = milestone.contract
    
    # Проверяем, что пользователь является клиентом
    if request.user != contract.client:
        messages.error(request, _("You are not authorized to create escrow payments"))
        return redirect('jobs:contract_detail', pk=contract.pk)
    
    # Проверяем, что веха не имеет активного эскроу-платежа
    try:
        escrow = milestone.escrow_payment
        messages.error(request, _("This milestone already has an escrow payment"))
        return redirect('jobs:contract_detail', pk=contract.pk)
    except:
        pass
    
    # Создаем эскроу-платеж
    escrow = EscrowPayment.objects.create(
        milestone=milestone,
        amount=milestone.amount
    )
    
    messages.success(request, _("Escrow payment created successfully"))
    return redirect('payments:fund_escrow', escrow_id=escrow.escrow_id)

@login_required
def fund_escrow(request, escrow_id):
    """
    Пополнение эскроу-платежа
    """
    escrow = get_object_or_404(EscrowPayment, escrow_id=escrow_id)
    milestone = escrow.milestone
    contract = milestone.contract
    
    # Проверяем, что пользователь является клиентом
    if request.user != contract.client:
        messages.error(request, _("You are not authorized to fund this escrow payment"))
        return redirect('jobs:contract_detail', pk=contract.pk)
    
    # Проверяем, что эскроу ещё не пополнен
    if escrow.status != 'pending':
        messages.error(request, _("This escrow payment is already funded or completed"))
        return redirect('jobs:contract_detail', pk=contract.pk)
    
    if request.method == 'POST':
        # Проверяем баланс кошелька
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        
        if wallet.balance < escrow.amount:
            messages.error(request, _("Insufficient funds in your wallet"))
            return redirect('payments:deposit')
        
        try:
            with db_transaction.atomic():
                # Снимаем средства с кошелька клиента
                description = _("Escrow payment for milestone: {}").format(milestone.title)
                transaction = wallet.withdraw(
                    amount=escrow.amount,
                    description=description,
                    contract=contract,
                    milestone=milestone
                )
                
                # Пополняем эскроу
                escrow.fund(client_transaction=transaction)
                
                # Обновляем статус вехи
                milestone.is_escrow_funded = True
                milestone.save()
                
                messages.success(request, _("Escrow payment funded successfully"))
                return redirect('jobs:contract_detail', pk=contract.pk)
        except ValueError as e:
            messages.error(request, str(e))
    
    context = {
        'escrow': escrow,
        'milestone': milestone,
        'contract': contract,
    }
    
    return render(request, 'payments/fund_escrow.html', context)

@login_required
def release_escrow(request, escrow_id):
    """
    Выплата средств из эскроу фрилансеру
    """
    escrow = get_object_or_404(EscrowPayment, escrow_id=escrow_id)
    milestone = escrow.milestone
    contract = milestone.contract
    
    # Проверяем, что пользователь является клиентом
    if request.user != contract.client:
        messages.error(request, _("You are not authorized to release this escrow payment"))
        return redirect('jobs:contract_detail', pk=contract.pk)
    
    # Проверяем, что эскроу пополнен
    if escrow.status != 'funded':
        messages.error(request, _("This escrow payment cannot be released"))
        return redirect('jobs:contract_detail', pk=contract.pk)
    
    if request.method == 'POST':
        try:
            with db_transaction.atomic():
                # Выплачиваем средства фрилансеру
                escrow.release()
                
                # Обновляем статус вехи
                milestone.is_paid = True
                milestone.paid_at = timezone.now()
                milestone.save()
                
                messages.success(request, _("Funds released to freelancer successfully"))
                return redirect('jobs:contract_detail', pk=contract.pk)
        except ValueError as e:
            messages.error(request, str(e))
    
    context = {
        'escrow': escrow,
        'milestone': milestone,
        'contract': contract,
    }
    
    return render(request, 'payments/release_escrow.html', context)

@login_required
def refund_escrow(request, escrow_id):
    """
    Возврат средств из эскроу клиенту
    """
    escrow = get_object_or_404(EscrowPayment, escrow_id=escrow_id)
    milestone = escrow.milestone
    contract = milestone.contract
    
    # Проверяем, что пользователь является клиентом или админом
    if request.user != contract.client and not request.user.is_staff:
        messages.error(request, _("You are not authorized to refund this escrow payment"))
        return redirect('jobs:contract_detail', pk=contract.pk)
    
    # Проверяем, что эскроу пополнен или в статусе спора
    if escrow.status not in ['funded', 'disputed']:
        messages.error(request, _("This escrow payment cannot be refunded"))
        return redirect('jobs:contract_detail', pk=contract.pk)
    
    if request.method == 'POST':
        try:
            with db_transaction.atomic():
                # Возвращаем средства клиенту
                escrow.refund()
                
                # Обновляем статус вехи
                milestone.is_escrow_funded = False
                milestone.save()
                
                messages.success(request, _("Funds refunded to client successfully"))
                return redirect('jobs:contract_detail', pk=contract.pk)
        except ValueError as e:
            messages.error(request, str(e))
    
    context = {
        'escrow': escrow,
        'milestone': milestone,
        'contract': contract,
    }
    
    return render(request, 'payments/refund_escrow.html', context)

@login_required
def dispute_escrow(request, escrow_id):
    """
    Создание спора по эскроу-платежу
    """
    escrow = get_object_or_404(EscrowPayment, escrow_id=escrow_id)
    milestone = escrow.milestone
    contract = milestone.contract
    
    # Проверяем, что пользователь является участником контракта
    if request.user != contract.client and request.user != contract.freelancer:
        messages.error(request, _("You are not authorized to dispute this escrow payment"))
        return redirect('jobs:contract_detail', pk=contract.pk)
    
    # Проверяем, что эскроу пополнен
    if escrow.status != 'funded':
        messages.error(request, _("This escrow payment cannot be disputed"))
        return redirect('jobs:contract_detail', pk=contract.pk)
    
    if request.method == 'POST':
        try:
            with db_transaction.atomic():
                # Создаем спор
                escrow.dispute()
                
                # Отправляем уведомления администраторам
                # (здесь можно добавить код для отправки уведомлений)
                
                messages.success(request, _("Dispute created successfully. An administrator will review your case."))
                return redirect('jobs:contract_detail', pk=contract.pk)
        except ValueError as e:
            messages.error(request, str(e))
    
    context = {
        'escrow': escrow,
        'milestone': milestone,
        'contract': contract,
    }
    
    return render(request, 'payments/dispute_escrow.html', context) 