from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.translation import get_language
from jobs.models import Contract, Milestone
import uuid
import json
from decimal import Decimal

class Transaction(models.Model):
    """
    Базовая модель для финансовых транзакций
    """
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('refunded', _('Refunded')),
    )
    
    TRANSACTION_TYPES = (
        ('deposit', _('Deposit')),          # Пополнение счета
        ('withdrawal', _('Withdrawal')),    # Вывод средств
        ('payment', _('Payment')),          # Оплата за работу
        ('refund', _('Refund')),           # Возврат средств
        ('fee', _('Service Fee')),         # Комиссия сервиса
    )
    
    transaction_id = models.CharField(_('Transaction ID'), max_length=50, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    amount = models.DecimalField(_('Amount'), max_digits=10, decimal_places=2)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_type = models.CharField(_('Type'), max_length=20, choices=TRANSACTION_TYPES)
    description = models.TextField(_('Description'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    reference_id = models.CharField(_('External Reference ID'), max_length=100, blank=True, null=True)
    _meta_data = models.TextField(_('Meta Data'), blank=True, null=True)
    payment_method = models.CharField(_('Payment Method'), max_length=50, blank=True, null=True)
    
    # Для связи с договором или вехой (опционально)
    contract = models.ForeignKey(Contract, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    milestone = models.ForeignKey(Milestone, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    
    # Для связи с другими транзакциями (например, возврат средств ссылается на исходную транзакцию)
    related_transaction = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='related_transactions')
    
    class Meta:
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transactions')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.transaction_id} - {self.amount} ({self.get_transaction_type_display()})"
    
    def save(self, *args, **kwargs):
        # Генерируем уникальный ID транзакции
        if not self.transaction_id:
            uid = str(uuid.uuid4()).replace('-', '')[:10]
            self.transaction_id = f"TX-{uid}"
        super().save(*args, **kwargs)
    
    @property
    def meta_data(self):
        if self._meta_data:
            try:
                return json.loads(self._meta_data)
            except json.JSONDecodeError:
                return {}
        return {}
    
    @meta_data.setter
    def meta_data(self, value):
        self._meta_data = json.dumps(value)

class WithdrawalMethod(models.Model):
    """
    Методы вывода средств для пользователей
    """
    METHOD_CHOICES = (
        ('bank_transfer', _('Bank Transfer')),
        ('yoomoney', _('YooMoney')),
        ('kaspi', _('Kaspi Bank')),
        ('paypal', _('PayPal')),
        ('crypto', _('Cryptocurrency')),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='withdrawal_methods'
    )
    method_type = models.CharField(_('Method Type'), max_length=20, choices=METHOD_CHOICES)
    name = models.CharField(_('Name'), max_length=100)  # Имя/название метода вывода
    details = models.JSONField(_('Details'))  # JSON для хранения деталей (номер счета, email и т.д.)
    is_default = models.BooleanField(_('Default'), default=False)
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Withdrawal Method')
        verbose_name_plural = _('Withdrawal Methods')
        unique_together = ('user', 'name')
    
    def __str__(self):
        return f"{self.get_method_type_display()}: {self.name}"
    
    def save(self, *args, **kwargs):
        # Если метод становится дефолтным, убираем этот статус у других методов
        if self.is_default:
            WithdrawalMethod.objects.filter(
                user=self.user, 
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        
        super().save(*args, **kwargs)

class WithdrawalRequest(models.Model):
    """
    Запросы на вывод средств
    """
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('completed', _('Completed')),
    )
    
    request_id = models.CharField(_('Request ID'), max_length=50, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='withdrawal_requests'
    )
    amount = models.DecimalField(_('Amount'), max_digits=10, decimal_places=2)
    withdrawal_method = models.ForeignKey(
        WithdrawalMethod,
        on_delete=models.SET_NULL,
        null=True,
        related_name='withdrawal_requests'
    )
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    comment = models.TextField(_('Comment'), blank=True)
    admin_comment = models.TextField(_('Admin Comment'), blank=True)
    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='withdrawal_request'
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    completed_at = models.DateTimeField(_('Completed At'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Withdrawal Request')
        verbose_name_plural = _('Withdrawal Requests')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.request_id} - {self.amount} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        # Генерируем уникальный ID запроса
        if not self.request_id:
            uid = str(uuid.uuid4()).replace('-', '')[:10]
            self.request_id = f"WR-{uid}"
        
        # Устанавливаем дату завершения при изменении статуса
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        
        super().save(*args, **kwargs)

class Wallet(models.Model):
    """
    Электронный кошелек пользователя
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet'
    )
    balance = models.DecimalField(_('Balance'), max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Wallet')
        verbose_name_plural = _('Wallets')
    
    def __str__(self):
        return f"Wallet of {self.user.username}"
    
    def deposit(self, amount, description="", related_transaction=None, contract=None, milestone=None):
        """
        Метод для пополнения кошелька
        """
        if amount <= 0:
            raise ValueError(_("Amount must be positive"))
        
        # Создаем транзакцию
        transaction = Transaction.objects.create(
            user=self.user,
            amount=amount,
            transaction_type='deposit',
            status='completed',
            description=description,
            related_transaction=related_transaction,
            payment_method='system',
            contract=contract,
            milestone=milestone
        )
        
        # Сохраняем локализованное описание в зависимости от текущего языка
        current_language = get_language() or settings.LANGUAGE_CODE
        if current_language != settings.LANGUAGE_CODE:
            setattr(transaction, f'description_{current_language}', description)
            transaction.save(update_fields=[f'description_{current_language}'])
        
        # Обновляем баланс
        self.balance += amount
        self.save()
        
        return transaction
    
    def withdraw(self, amount, description="", related_transaction=None, contract=None, milestone=None):
        """
        Метод для вывода средств
        """
        if amount <= 0:
            raise ValueError(_("Amount must be positive"))
        
        if self.balance < amount:
            raise ValueError(_("Insufficient funds"))
        
        # Создаем транзакцию
        transaction = Transaction.objects.create(
            user=self.user,
            amount=amount,
            transaction_type='withdrawal',
            status='completed',
            description=description,
            related_transaction=related_transaction,
            contract=contract,
            milestone=milestone,
            payment_method='system'
        )
        
        # Сохраняем локализованное описание в зависимости от текущего языка
        current_language = get_language() or settings.LANGUAGE_CODE
        if current_language != settings.LANGUAGE_CODE:
            setattr(transaction, f'description_{current_language}', description)
            transaction.save(update_fields=[f'description_{current_language}'])
        
        # Обновляем баланс
        self.balance -= amount
        self.save()
        
        return transaction
    
    def payment(self, amount, contract, milestone=None, description=""):
        """
        Метод для выполнения оплаты по контракту/вехе
        """
        if amount <= 0:
            raise ValueError(_("Amount must be positive"))
        
        if self.balance < amount:
            raise ValueError(_("Insufficient funds"))
        
        # Создаем транзакцию
        transaction = Transaction.objects.create(
            user=self.user,
            amount=amount,
            transaction_type='payment',
            status='completed',
            description=description,
            contract=contract,
            milestone=milestone,
            payment_method='system'
        )
        
        # Сохраняем локализованное описание в зависимости от текущего языка
        current_language = get_language() or settings.LANGUAGE_CODE
        if current_language != settings.LANGUAGE_CODE:
            setattr(transaction, f'description_{current_language}', description)
            transaction.save(update_fields=[f'description_{current_language}'])
        
        # Расчет комиссии сервиса (5%)
        service_fee = amount * Decimal('0.05')
        
        # Обновляем баланс текущего пользователя (клиента)
        self.balance -= amount
        self.save()
        
        return transaction

class EscrowPayment(models.Model):
    """
    Модель для эскроу-платежей (условного депонирования)
    """
    STATUS_CHOICES = (
        ('pending', _('Pending')),           # Ожидает пополнения
        ('funded', _('Funded')),             # Средства депонированы
        ('released', _('Released')),         # Средства выплачены фрилансеру
        ('refunded', _('Refunded')),         # Средства возвращены клиенту
        ('disputed', _('Disputed')),         # Спорная ситуация
        ('cancelled', _('Cancelled')),       # Отменен
    )
    
    escrow_id = models.CharField(_('Escrow ID'), max_length=50, unique=True, editable=False)
    milestone = models.OneToOneField(
        'jobs.Milestone',
        on_delete=models.CASCADE,
        related_name='escrow_payment'
    )
    amount = models.DecimalField(_('Amount'), max_digits=10, decimal_places=2)
    client_transaction = models.ForeignKey(
        Transaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='client_escrow_payments'
    )
    freelancer_transaction = models.ForeignKey(
        Transaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='freelancer_escrow_payments'
    )
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    funded_at = models.DateTimeField(_('Funded At'), null=True, blank=True)
    released_at = models.DateTimeField(_('Released At'), null=True, blank=True)
    refunded_at = models.DateTimeField(_('Refunded At'), null=True, blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Escrow Payment')
        verbose_name_plural = _('Escrow Payments')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Escrow {self.escrow_id} for {self.milestone.title}"
    
    def save(self, *args, **kwargs):
        # Генерируем уникальный ID эскроу, если его нет
        if not self.escrow_id:
            uid = str(uuid.uuid4()).replace('-', '')[:10]
            self.escrow_id = f"ES-{uid}"
        super().save(*args, **kwargs)
    
    @classmethod
    def create_escrow(cls, milestone, fund_immediately=False):
        """
        Создает новый эскроу-платеж для вехи и при необходимости сразу пополняет его
        
        Аргументы:
        - milestone: объект Milestone
        - fund_immediately: если True, сразу пополняет эскроу с кошелька клиента
        
        Возвращает:
        - объект EscrowPayment
        - None, если произошла ошибка
        """
        from django.db import transaction
        
        try:
            # Проверяем, что веха существует
            if not milestone:
                raise ValueError(_("Milestone not provided"))
            
            # Проверяем, что еще нет эскроу для этой вехи
            if hasattr(milestone, 'escrow_payment'):
                return milestone.escrow_payment
            
            contract = milestone.contract
            client = contract.client
            
            # Проверяем, что клиент есть и у него есть кошелек
            if not client:
                raise ValueError(_("Client not found for this milestone"))
                
            client_wallet, created = Wallet.objects.get_or_create(user=client)
            
            # Создаем новый эскроу-платеж с атомарной транзакцией
            with transaction.atomic():
                escrow = cls.objects.create(
                    milestone=milestone,
                    amount=milestone.amount
                )
                
                # Если запрошено немедленное пополнение - выполняем его
                if fund_immediately:
                    # Проверяем достаточно ли средств
                    if client_wallet.balance < milestone.amount:
                        raise ValueError(_("Insufficient funds in client's wallet"))
                    
                    # Создаем транзакцию для списания средств
                    client_transaction = Transaction.objects.create(
                        user=client,
                        amount=milestone.amount,
                        transaction_type='payment',
                        status='completed',
                        description=_("Escrow funding for milestone: {}").format(milestone.title),
                        payment_method='wallet',
                        contract=contract,
                        milestone=milestone
                    )
                    
                    # Обновляем баланс клиента
                    client_wallet.balance -= milestone.amount
                    client_wallet.save()
                    
                    # Обновляем статус эскроу
                    escrow.client_transaction = client_transaction
                    escrow.status = 'funded'
                    escrow.funded_at = timezone.now()
                    escrow.save()
                    
                    # Обновляем статус вехи
                    milestone.payment_status = 'escrow'
                    milestone.save()
                
                return escrow
        except Exception as e:
            import logging
            logger = logging.getLogger('payments')
            logger.error(f"Error creating escrow payment: {str(e)}", exc_info=True)
            return None

    def fund(self, client_transaction):
        """
        Пополняет эскроу-платеж
        """
        if self.status != 'pending':
            raise ValueError(_("Can only fund pending escrow payments"))
        
        self.client_transaction = client_transaction
        self.status = 'funded'
        self.funded_at = timezone.now()
        self.save()
        
        # Обновляем статус вехи
        self.milestone.payment_status = 'escrow'
        self.milestone.save()
        
        return True
    
    def release(self, description=""):
        """
        Выплата средств фрилансеру
        """
        if self.status != 'funded':
            raise ValueError(_("Cannot release funds: escrow payment is not in funded state"))
        
        contract = self.milestone.contract
        freelancer = contract.freelancer
        
        # Создаем транзакцию для фрилансера и пополняем его кошелек
        wallet, _ = Wallet.objects.get_or_create(user=freelancer)
        
        # Ищем transaction_id в связанной транзакции или создаем новый
        transaction = wallet.deposit(
            amount=self.amount,
            description=_("Payment for milestone: {}").format(self.milestone.title) if not description else description,
            related_transaction=self.client_transaction
        )
        
        # Обновляем модель эскроу
        self.freelancer_transaction = transaction
        self.status = 'released'
        self.released_at = timezone.now()
        self.save()
        
        # Обновляем веху
        milestone = self.milestone
        milestone.status = 'approved'
        milestone.save()
        
        return transaction
    
    def refund(self, description=""):
        """
        Возврат средств клиенту
        """
        if self.status not in ['funded', 'disputed']:
            raise ValueError(_("Cannot refund: escrow payment is not in funded or disputed state"))
        
        contract = self.milestone.contract
        client = contract.client
        
        # Создаем транзакцию для клиента и пополняем его кошелек
        wallet, _ = Wallet.objects.get_or_create(user=client)
        transaction = wallet.deposit(
            amount=self.amount,
            description=_("Refund for milestone: {}").format(self.milestone.title) if not description else description,
            related_transaction=self.client_transaction,
            contract=contract,
            milestone=self.milestone
        )
        
        # Обновляем модель эскроу
        self.status = 'refunded'
        self.refunded_at = timezone.now()
        self.save()
        
        # Обновляем веху
        milestone = self.milestone
        milestone.status = 'cancelled'
        milestone.save()
        
        return transaction
    
    def dispute(self):
        """
        Перевод платежа в статус спора
        """
        if self.status != 'funded':
            raise ValueError(_("Cannot dispute: escrow payment is not in funded state"))
        
        self.status = 'disputed'
        self.save() 