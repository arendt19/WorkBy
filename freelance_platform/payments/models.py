from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.translation import get_language
from jobs.models import Contract, Milestone
import uuid
import json

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
    
    def deposit(self, amount, description="", related_transaction=None):
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
            related_transaction=related_transaction
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
    
    def withdraw(self, amount, description="", related_transaction=None):
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
            related_transaction=related_transaction
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
            milestone=milestone
        )
        
        # Сохраняем локализованное описание в зависимости от текущего языка
        current_language = get_language() or settings.LANGUAGE_CODE
        if current_language != settings.LANGUAGE_CODE:
            setattr(transaction, f'description_{current_language}', description)
            transaction.save(update_fields=[f'description_{current_language}'])
        
        # Расчет комиссии сервиса (например, 5%)
        service_fee = amount * 0.05
        
        # Обновляем баланс текущего пользователя (клиента)
        self.balance -= amount
        self.save()
        
        return transaction 