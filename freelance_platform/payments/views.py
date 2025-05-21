from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db import transaction as db_transaction
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta
from django.utils.translation import get_language
from decimal import Decimal, InvalidOperation
import logging

from .models import Transaction, Wallet, WithdrawalMethod, WithdrawalRequest, EscrowPayment
from .forms import DepositForm, WithdrawForm, TransactionFilterForm, TopUpForm, PaymentMethodForm, WithdrawalMethodForm
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

# Настраиваем логгер
logger = logging.getLogger('payments')

@login_required
def wallet_view(request):
    """
    Страница кошелька пользователя с балансом и историей транзакций
    """
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    # Получаем недавние транзакции
    recent_transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    # Получаем методы вывода
    withdrawal_methods = WithdrawalMethod.objects.filter(user=request.user, is_active=True).order_by('-is_default')[:3]
    
    # Считаем статистику для отображения
    total_in = Transaction.objects.filter(
        user=request.user,
        transaction_type__in=['deposit', 'refund'],
        status='completed'
    ).aggregate(sum=Sum('amount'))['sum'] or 0
    
    total_out = Transaction.objects.filter(
        user=request.user,
        transaction_type__in=['withdrawal', 'payment'],
        status='completed'
    ).aggregate(sum=Sum('amount'))['sum'] or 0
    
    # Статистика по эскроу-платежам
    in_escrow = 0
    try:
        if hasattr(request.user, 'client_contracts'):
            # Для клиентов - сумма средств в эскроу
            client_contracts = request.user.client_contracts.all()
            for contract in client_contracts:
                escrow_payments = EscrowPayment.objects.filter(
                    milestone__contract=contract,
                    status='funded'
                )
                in_escrow += escrow_payments.aggregate(sum=Sum('amount'))['sum'] or 0
    except Exception as e:
        logger.error(f"Error calculating escrow amount for user {request.user.id}: {str(e)}")
    
    # Сумма в ожидании
    pending = Transaction.objects.filter(
        user=request.user,
        status='pending'
    ).aggregate(sum=Sum('amount'))['sum'] or 0
    
    stats = {
        'total_in': total_in,
        'total_out': total_out,
        'in_escrow': in_escrow,
        'pending': pending
    }
    
    context = {
        'wallet': wallet,
        'recent_transactions': recent_transactions,
        'stats': stats,
        'withdrawal_methods': withdrawal_methods
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
    Страница для вывода средств из кошелька
    """
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    withdrawal_methods = WithdrawalMethod.objects.filter(user=request.user, is_active=True)
    
    # Проверяем, что у пользователя есть средства для вывода
    if wallet.balance <= 0:
        messages.warning(request, _("You don't have any funds to withdraw"))
        return redirect('payments:wallet')
    
    if request.method == 'POST':
        form = WithdrawForm(request.POST, user=request.user)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            withdrawal_method = form.cleaned_data['withdrawal_method']
            comment = form.cleaned_data.get('comment', '')
            
            # Проверяем, достаточно ли средств
            if amount > wallet.balance:
                messages.error(request, _("Insufficient funds. Your current balance is {}").format(wallet.balance))
                return redirect('payments:withdraw')
            
            try:
                # Создаем запрос на вывод средств
                withdrawal_request = WithdrawalRequest.objects.create(
                    user=request.user,
                    amount=amount,
                    withdrawal_method=withdrawal_method,
                    comment=comment
                )
                
                # Создаем транзакцию в статусе pending
                transaction = Transaction.objects.create(
                    user=request.user,
                    amount=amount,
                    transaction_type='withdrawal',
                    status='pending',
                    description=_("Withdrawal request"),
                    payment_method=withdrawal_method.method_type
                )
                
                # Привязываем транзакцию к запросу
                withdrawal_request.transaction = transaction
                withdrawal_request.save()
                
                # Резервируем средства (уменьшаем доступный баланс, но еще не списываем)
                wallet.balance -= amount
                wallet.save()
                
                messages.success(
                    request, 
                    _("Withdrawal request for {} created successfully. Your funds will be transferred within 2-3 business days.").format(amount)
                )
                return redirect('payments:wallet')
            
            except Exception as e:
                logger.error(f"Error creating withdrawal request: {str(e)}", exc_info=True)
                messages.error(request, _("An error occurred while processing your withdrawal request. Please try again later."))
    else:
        # Инициализируем форму с текущими данными пользователя
        form = WithdrawForm(user=request.user, initial={
            'amount': Decimal('0.00'),
            'withdrawal_method': withdrawal_methods.filter(is_default=True).first()
        })
    
    # Получаем историю запросов на вывод средств
    withdrawal_history = WithdrawalRequest.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Расчитываем максимальную доступную сумму для вывода
    max_available = wallet.balance
    
    # Проверяем, есть ли у пользователя методы вывода
    has_withdrawal_methods = withdrawal_methods.exists()
    
    context = {
        'wallet': wallet,
        'form': form,
        'withdrawal_methods': withdrawal_methods,
        'max_available': max_available,
        'has_withdrawal_methods': has_withdrawal_methods,
        'withdrawal_history': withdrawal_history
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

@login_required
def yoomoney_initiate_payment(request):
    """
    Инициирует платеж через ЮMoney
    """
    # Валидация суммы
    try:
        amount = Decimal(request.GET.get('amount', '0'))
        if amount <= 0:
            messages.error(request, _('Invalid payment amount'))
            return redirect('payments:deposit')
    except (ValueError, TypeError, InvalidOperation):
        messages.error(request, _('Invalid payment amount format'))
        return redirect('payments:deposit')
    
    # Успешный URL для возврата
    success_url = request.build_absolute_uri(reverse('payments:yoomoney_success_callback'))
    
    # Создаем метаданные для идентификации пользователя
    metadata = {
        'user_id': request.user.id,
        'username': request.user.username,
        'payment_type': 'deposit'
    }
    
    try:
        # Создаем платеж через API
        yoomoney_api = YooMoneyAPI()
        payment_data = yoomoney_api.create_payment(
            amount=amount,
            return_url=success_url,
            description=_("Deposit to WorkBy account: {}").format(request.user.username),
            metadata=metadata
        )
        
        # Сохраняем транзакцию в статусе "pending"
        Transaction.objects.create(
            user=request.user,
            amount=amount,
            transaction_type='deposit',
            status='pending',
            description=_("YooMoney deposit"),
            reference_id=payment_data.get('id'),
            payment_method='yoomoney',
            _meta_data=json.dumps(payment_data)
        )
        
        # Получаем URL для перенаправления пользователя
        confirmation_url = payment_data.get('confirmation', {}).get('confirmation_url')
        if not confirmation_url:
            logger.error(f"YooMoney payment error: No confirmation URL returned. Payment data: {payment_data}")
            messages.error(request, _('Error initiating payment. Please try again.'))
            return redirect('payments:deposit')
        
        return redirect(confirmation_url)
    except Exception as e:
        logger.error(f"YooMoney payment error: {str(e)}")
        messages.error(request, _('Error initiating payment: {}').format(str(e)))
        return redirect('payments:deposit')

@require_GET
def yoomoney_success_callback(request):
    """
    Обработчик успешного платежа через ЮMoney (redirect после оплаты)
    """
    payment_id = request.GET.get('payment_id', '')
    
    if not payment_id:
        messages.error(request, _('Invalid payment information received'))
        return redirect('payments:wallet')
    
    try:
        # Проверяем статус платежа
        yoomoney_api = YooMoneyAPI()
        payment_info = yoomoney_api.get_payment_status(payment_id)
        
        if payment_info.get('status') != 'succeeded':
            logger.warning(f"Payment {payment_id} not succeeded yet. Status: {payment_info.get('status')}")
            messages.warning(request, _('Your payment is being processed. We will update your balance once the payment is confirmed.'))
            return redirect('payments:wallet')
        
        # Получаем связанную транзакцию
        transaction = Transaction.objects.filter(
            reference_id=payment_id,
            status='pending'
        ).first()
        
        if not transaction:
            # Если транзакция не найдена - возможно, она уже была обработана
            completed_transaction = Transaction.objects.filter(
                reference_id=payment_id,
                status='completed'
            ).first()
            
            if completed_transaction:
                messages.success(request, _('Your payment has already been processed. Thank you!'))
                return redirect('payments:wallet')
            
            # Пытаемся получить пользователя из метаданных платежа
            metadata = payment_info.get('metadata', {})
            user_id = metadata.get('user_id')
            
            if not user_id or not request.user.is_authenticated or int(user_id) != request.user.id:
                logger.error(f"Cannot identify user for payment {payment_id}. Metadata: {metadata}")
                messages.error(request, _('Could not identify the payment. Please contact support.'))
                return redirect('payments:wallet')
            
            # Создаем транзакцию задним числом
            transaction = Transaction.objects.create(
                user=request.user,
                amount=Decimal(payment_info.get('amount', {}).get('value', '0')),
                transaction_type='deposit',
                status='pending',
                description=_("YooMoney deposit"),
                reference_id=payment_id,
                payment_method='yoomoney',
                _meta_data=json.dumps(payment_info)
            )
            logger.info(f"Created transaction {transaction.transaction_id} for existing payment {payment_id}")
        
        # Если транзакция уже завершена, возвращаем пользователя в кошелек
        if transaction.status == 'completed':
            messages.success(request, _('Your payment has been processed. Thank you!'))
            return redirect('payments:wallet')
        
        # Обновляем кошелек пользователя
        with db_transaction.atomic():
            amount = Decimal(payment_info.get('amount', {}).get('value', '0'))
            wallet, created = Wallet.objects.get_or_create(user=transaction.user)
            
            # Обновляем статус транзакции
            transaction.status = 'completed'
            transaction._meta_data = json.dumps(payment_info)  # Обновляем метаданные
            transaction.save()
            
            # Пополняем кошелек
            wallet.balance += amount
            wallet.save()
            
            logger.info(f"Successfully processed payment {payment_id} for user {transaction.user.username}, amount: {amount}")
            
            messages.success(request, _('Payment successful! Your balance has been updated.'))
        
        return redirect('payments:wallet')
    except Exception as e:
        logger.error(f"Error processing YooMoney payment callback: {str(e)}", exc_info=True)
        messages.error(request, _('Error processing your payment. Please check your balance or contact support.'))
        return redirect('payments:wallet')

@csrf_exempt
@require_POST
def yoomoney_notification_callback(request):
    """
    Обработчик webhook-уведомлений от ЮMoney
    """
    try:
        # Получаем данные уведомления
        notification_data = request.body.decode('utf-8')
        signature = request.headers.get('Signature')
        
        # Логируем получение уведомления
        logger.info(f"Received YooMoney notification: {notification_data[:100]}...")
        
        # Верифицируем подпись
        yoomoney_api = YooMoneyAPI()
        if not yoomoney_api.verify_notification(notification_data, signature):
            logger.warning(f"Invalid YooMoney notification signature: {signature}")
            return HttpResponse(status=401)
        
        # Парсим JSON данные
        payment_data = json.loads(notification_data)
        payment_id = payment_data.get('object', {}).get('id')
        
        if not payment_id:
            logger.error("Invalid YooMoney notification format, missing payment ID")
            return HttpResponse(status=400)
        
        # Получаем связанную транзакцию
        transaction = Transaction.objects.filter(
            reference_id=payment_id
        ).first()
        
        # Если событие - успешная оплата
        if payment_data.get('event') == 'payment.succeeded':
            # Если транзакция не найдена, пытаемся восстановить по metadata
            if not transaction:
                metadata = payment_data.get('object', {}).get('metadata', {})
                user_id = metadata.get('user_id')
                
                if not user_id:
                    logger.error(f"Cannot identify user for payment {payment_id}. Metadata: {metadata}")
                    return HttpResponse(status=200)  # Возвращаем 200 чтобы не получать повторные уведомления
                
                from django.contrib.auth import get_user_model
                User = get_user_model()
                
                try:
                    user = User.objects.get(id=user_id)
                    
                    # Создаем транзакцию задним числом
                    amount = Decimal(payment_data.get('object', {}).get('amount', {}).get('value', '0'))
                    transaction = Transaction.objects.create(
                        user=user,
                        amount=amount,
                        transaction_type='deposit',
                        status='pending',  # Будет обновлено ниже
                        description=_("YooMoney deposit (webhook)"),
                        reference_id=payment_id,
                        payment_method='yoomoney',
                        _meta_data=json.dumps(payment_data.get('object', {}))
                    )
                    logger.info(f"Created transaction {transaction.transaction_id} from webhook for payment {payment_id}")
                except User.DoesNotExist:
                    logger.error(f"User with ID {user_id} not found for payment {payment_id}")
                    return HttpResponse(status=200)  # Возвращаем 200 чтобы не получать повторные уведомления
            
            # Если транзакция уже завершена, игнорируем уведомление
            if transaction and transaction.status == 'completed':
                logger.info(f"Transaction {transaction.transaction_id} already completed, ignoring webhook")
                return HttpResponse(status=200)
            
            # Обрабатываем успешный платеж
            if transaction:
                with db_transaction.atomic():
                    amount = Decimal(payment_data.get('object', {}).get('amount', {}).get('value', '0'))
                    wallet, created = Wallet.objects.get_or_create(user=transaction.user)
                    
                    # Обновляем статус транзакции
                    transaction.status = 'completed'
                    transaction._meta_data = json.dumps(payment_data.get('object', {}))
                    transaction.save()
                    
                    # Пополняем кошелек
                    wallet.balance += amount
                    wallet.save()
                    
                    logger.info(f"Successfully processed webhook payment {payment_id} for user {transaction.user.username}, amount: {amount}")
        
        # Если событие - отмена платежа
        elif payment_data.get('event') == 'payment.canceled':
            if transaction and transaction.status == 'pending':
                transaction.status = 'failed'
                transaction._meta_data = json.dumps(payment_data.get('object', {}))
                transaction.save()
                logger.info(f"Payment {payment_id} marked as failed due to cancellation")
        
        return HttpResponse(status=200)
    except Exception as e:
        logger.error(f"Error processing YooMoney webhook: {str(e)}", exc_info=True)
        return HttpResponse(status=500)

@login_required
def create_escrow_payment(request, milestone_id):
    """
    Создание эскроу-платежа для вехи
    """
    milestone = get_object_or_404(Milestone, pk=milestone_id)
    contract = milestone.contract
    
    # Проверяем, что пользователь является клиентом контракта
    if contract.client != request.user:
        messages.error(request, _("You do not have permission to create an escrow payment for this milestone"))
        return redirect('jobs:contract_detail', pk=contract.pk)
    
    # Проверяем, что еще нет эскроу для этой вехи
    if hasattr(milestone, 'escrow_payment'):
        messages.info(request, _("An escrow payment already exists for this milestone"))
        return redirect('payments:fund_escrow', escrow_id=milestone.escrow_payment.escrow_id)
    
    # Проверяем состояние вехи
    if milestone.payment_status == 'paid':
        messages.error(request, _("This milestone is already paid"))
        return redirect('jobs:contract_detail', pk=contract.pk)
    
    # Если это POST-запрос, создаем эскроу-платеж и пополняем его, если указано
    if request.method == 'POST':
        # Проверяем, нужно ли сразу пополнить эскроу
        fund_immediately = request.POST.get('fund_immediately') == 'yes'
        
        # Получаем кошелек клиента и проверяем доступность средств
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        
        if fund_immediately and wallet.balance < milestone.amount:
            messages.error(
                request, 
                _("Insufficient funds in your wallet. Please add funds first. Required: {}, Available: {}").format(
                    milestone.amount, wallet.balance
                )
            )
            return redirect('payments:wallet')
        
        try:
            # Создаем эскроу-платеж с использованием класс-метода
            escrow = EscrowPayment.create_escrow(milestone, fund_immediately)
            
            if not escrow:
                messages.error(request, _("Failed to create escrow payment. Please try again."))
                return redirect('jobs:contract_detail', pk=contract.pk)
            
            if fund_immediately:
                messages.success(
                    request, 
                    _("Escrow payment created and funded successfully. Funds are now in escrow.")
                )
            else:
                messages.success(
                    request, 
                    _("Escrow payment created successfully. Please fund it to proceed.")
                )
            
            return redirect('payments:fund_escrow', escrow_id=escrow.escrow_id)
        
        except Exception as e:
            messages.error(request, _("Error creating escrow payment: {}").format(str(e)))
            logger.error(f"Error in create_escrow_payment view: {str(e)}", exc_info=True)
            return redirect('jobs:contract_detail', pk=contract.pk)
    
    # Если это GET-запрос, показываем форму
    context = {
        'milestone': milestone,
        'contract': contract,
        'wallet': Wallet.objects.filter(user=request.user).first(),
        'freelancer': contract.freelancer
    }
    
    return render(request, 'payments/create_escrow.html', context)

@login_required
def fund_escrow(request, escrow_id):
    """
    Пополнение эскроу-платежа из кошелька пользователя
    """
    # Получаем эскроу-платеж
    escrow = get_object_or_404(EscrowPayment, escrow_id=escrow_id)
    milestone = escrow.milestone
    contract = milestone.contract
    
    # Проверяем, что пользователь является клиентом контракта
    if contract.client != request.user:
        messages.error(request, _("You do not have permission to fund this escrow payment"))
        return redirect('jobs:contract_detail', pk=contract.pk)
    
    # Проверяем, что эскроу в статусе ожидания
    if escrow.status != 'pending':
        messages.info(request, _("This escrow payment is already funded or completed"))
        return redirect('jobs:contract_detail', pk=contract.pk)
    
    # Получаем кошелек пользователя
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    # Проверяем, достаточно ли средств
    if wallet.balance < escrow.amount:
        messages.error(
            request, 
            _("Insufficient funds in your wallet. Please add funds first. Required: {}, Available: {}").format(
                escrow.amount, wallet.balance
            )
        )
        return redirect('payments:deposit')
    
    # Если это POST-запрос, обрабатываем пополнение эскроу
    if request.method == 'POST':
        # Проверяем подтверждение пользователя
        if not request.POST.get('confirm_funding'):
            messages.error(request, _("Please confirm that you want to fund this escrow payment"))
            return redirect('payments:fund_escrow', escrow_id=escrow_id)
        
        try:
            with db_transaction.atomic():
                # Создаем транзакцию для списания средств
                transaction = Transaction.objects.create(
                    user=request.user,
                    amount=escrow.amount,
                    transaction_type='payment',
                    status='completed',
                    description=_("Escrow funding for milestone: {}").format(milestone.title),
                    payment_method='wallet',
                    contract=contract,
                    milestone=milestone
                )
                
                # Списываем средства с кошелька
                wallet.balance -= escrow.amount
                wallet.save()
                
                # Пополняем эскроу
                escrow.fund(transaction)
                
                # Создаем уведомление для фрилансера
                from accounts.models import Notification
                Notification.objects.create(
                    user=contract.freelancer,
                    notification_type='escrow_funded',
                    title=_("Escrow Funded"),
                    content=_("The client has funded the escrow for milestone '{milestone}' in contract '{contract}'").format(
                        milestone=milestone.title,
                        contract=contract.title
                    ),
                    related_object_id=milestone.id,
                    related_object_type='milestone'
                )
                
                # Отправляем уведомление в чат, если он существует
                from chat.models import Conversation, Message
                conversation = Conversation.objects.filter(
                    participants=contract.client
                ).filter(
                    participants=contract.freelancer
                ).first()
                
                if conversation:
                    Message.objects.create(
                        conversation=conversation,
                        sender=request.user,
                        content=_("I have funded the escrow for milestone '{milestone}'. You can now start working on it!").format(
                            milestone=milestone.title
                        ),
                        is_system=True
                    )
                
                messages.success(request, _("Escrow payment funded successfully"))
                return redirect('jobs:contract_detail', pk=contract.pk)
                
        except Exception as e:
            messages.error(request, _("Error funding escrow payment: {}").format(str(e)))
            logger.error(f"Error in fund_escrow view: {str(e)}", exc_info=True)
            return redirect('payments:fund_escrow', escrow_id=escrow_id)
    
    # Если это GET-запрос, показываем форму
    context = {
        'escrow': escrow,
        'milestone': milestone,
        'contract': contract,
        'wallet': wallet
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

@login_required
def add_withdrawal_method(request):
    """
    Страница для добавления нового метода вывода средств
    """
    # Если это POST-запрос, обрабатываем форму
    if request.method == 'POST':
        form = WithdrawalMethodForm(request.POST)
        if form.is_valid():
            method = form.save(commit=False)
            method.user = request.user
            
            # Если это первый метод пользователя, делаем его методом по умолчанию
            if not WithdrawalMethod.objects.filter(user=request.user).exists():
                method.is_default = True
            
            # Если отмечен как метод по умолчанию, снимаем этот флаг у других методов
            elif method.is_default:
                WithdrawalMethod.objects.filter(user=request.user, is_default=True).update(is_default=False)
            
            method.save()
            
            messages.success(request, _("Withdrawal method added successfully"))
            return redirect('payments:manage_withdrawal_methods')
    else:
        # Инициализируем пустую форму
        form = WithdrawalMethodForm()
    
    context = {
        'form': form,
        'is_new': True
    }
    
    return render(request, 'payments/withdrawal_method_form.html', context)

@login_required
def edit_withdrawal_method(request, pk):
    """
    Страница для редактирования метода вывода средств
    """
    # Получаем метод пользователя или возвращаем 404
    method = get_object_or_404(WithdrawalMethod, pk=pk, user=request.user)
    
    # Если это POST-запрос, обрабатываем форму
    if request.method == 'POST':
        form = WithdrawalMethodForm(request.POST, instance=method)
        if form.is_valid():
            updated_method = form.save(commit=False)
            
            # Если отмечен как метод по умолчанию, снимаем этот флаг у других методов
            if updated_method.is_default:
                WithdrawalMethod.objects.filter(user=request.user, is_default=True).exclude(pk=pk).update(is_default=False)
            
            updated_method.save()
            
            messages.success(request, _("Withdrawal method updated successfully"))
            return redirect('payments:manage_withdrawal_methods')
    else:
        # Инициализируем форму с данными существующего метода
        form = WithdrawalMethodForm(instance=method)
    
    context = {
        'form': form,
        'method': method,
        'is_new': False
    }
    
    return render(request, 'payments/withdrawal_method_form.html', context)

@login_required
def delete_withdrawal_method(request, pk):
    """
    Удаление метода вывода средств
    """
    # Получаем метод пользователя или возвращаем 404
    method = get_object_or_404(WithdrawalMethod, pk=pk, user=request.user)
    
    # Проверяем, что это не единственный метод по умолчанию
    if method.is_default and WithdrawalMethod.objects.filter(user=request.user).count() > 1:
        # Находим другой метод и делаем его методом по умолчанию
        another_method = WithdrawalMethod.objects.filter(user=request.user).exclude(pk=pk).first()
        if another_method:
            another_method.is_default = True
            another_method.save()
    
    # Удаляем метод
    method.delete()
    
    messages.success(request, _("Withdrawal method deleted successfully"))
    return redirect('payments:manage_withdrawal_methods')

@login_required
def manage_withdrawal_methods(request):
    """
    Страница для управления всеми методами вывода средств пользователя
    """
    methods = WithdrawalMethod.objects.filter(user=request.user).order_by('-is_default', '-created_at')
    
    context = {
        'methods': methods
    }
    
    return render(request, 'payments/manage_withdrawal_methods.html', context)

@login_required
def set_default_withdrawal_method(request, pk):
    """
    Установка метода вывода средств по умолчанию
    """
    # Получаем метод пользователя или возвращаем 404
    method = get_object_or_404(WithdrawalMethod, pk=pk, user=request.user)
    
    # Снимаем флаг у текущего метода по умолчанию
    WithdrawalMethod.objects.filter(user=request.user, is_default=True).update(is_default=False)
    
    # Устанавливаем новый метод по умолчанию
    method.is_default = True
    method.save()
    
    messages.success(request, _("Default withdrawal method updated"))
    return redirect('payments:manage_withdrawal_methods')

@login_required
def withdrawal_history(request):
    """
    Страница истории запросов на вывод средств
    """
    withdrawal_requests = WithdrawalRequest.objects.filter(user=request.user).order_by('-created_at')
    
    # Фильтрация по статусу
    status_filter = request.GET.get('status')
    if status_filter and status_filter != 'all':
        withdrawal_requests = withdrawal_requests.filter(status=status_filter)
    
    context = {
        'withdrawal_requests': withdrawal_requests,
        'status_filter': status_filter if status_filter else 'all',
        'status_choices': WithdrawalRequest.STATUS_CHOICES
    }
    
    return render(request, 'payments/withdrawal_history.html', context)

@csrf_exempt
def yoomoney_webhook(request):
    """
    Webhook для приема уведомлений от YooMoney
    """
    if request.method != 'POST':
        return HttpResponse('Only POST method is allowed', status=405)
    
    # Получаем и валидируем данные от YooMoney
    try:
        payload = json.loads(request.body)
        notification_type = payload.get('notification_type')
        operation_id = payload.get('operation_id')
        amount = payload.get('amount')
        withdraw_amount = payload.get('withdraw_amount')
        label = payload.get('label')
        
        # Проверяем подпись уведомления, если она есть
        yoomoney_api = YooMoneyAPI()
        if not yoomoney_api.verify_notification(request.POST):
            logger.warning(f"Invalid YooMoney notification signature: {payload}")
            return HttpResponse('Invalid signature', status=400)
        
        logger.info(f"Received YooMoney webhook: {notification_type}, operation_id: {operation_id}")
        
        # Обрабатываем успешный платеж
        if notification_type == 'payment.succeeded':
            # Находим транзакцию по ID операции или метке
            transaction = Transaction.objects.filter(
                Q(external_id=operation_id) | Q(label=label),
                status='pending'
            ).first()
            
            if transaction:
                # Обновляем статус транзакции
                transaction.status = 'completed'
                transaction.external_id = operation_id
                transaction.save()
                
                # Обновляем баланс кошелька пользователя
                wallet, created = Wallet.objects.get_or_create(user=transaction.user)
                wallet.balance += Decimal(amount)
                wallet.save()
                
                # Отправляем уведомление пользователю
                from accounts.models import Notification
                Notification.objects.create(
                    user=transaction.user,
                    notification_type='payment_received',
                    title=_("Payment Received"),
                    content=_("Your payment of {amount} was successfully processed.").format(
                        amount=amount
                    )
                )
                
                return HttpResponse('Payment processed', status=200)
            else:
                logger.warning(f"Payment succeeded but transaction not found: {payload}")
                return HttpResponse('Transaction not found', status=404)
        
        # Другие типы уведомлений можно обработать по аналогии
        
        return HttpResponse('Notification received', status=200)
    
    except Exception as e:
        logger.error(f"Error processing YooMoney webhook: {str(e)}", exc_info=True)
        return HttpResponse('Error processing webhook', status=500) 