from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Transaction, WithdrawalMethod
from decimal import Decimal

class DepositForm(forms.Form):
    """
    Форма для пополнения кошелька
    """
    amount = forms.DecimalField(
        label=_('Amount'),
        min_value=100,
        max_value=100000,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter amount')
        })
    )

class WithdrawForm(forms.Form):
    """
    Форма для вывода средств
    """
    amount = forms.DecimalField(
        label=_('Amount'),
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('1000.00'),
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    
    withdrawal_method = forms.ModelChoiceField(
        label=_('Withdrawal Method'),
        queryset=WithdrawalMethod.objects.none(),
        empty_label=None,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    comment = forms.CharField(
        label=_('Comment (optional)'),
        max_length=200,
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': _('Additional information for the withdrawal')}),
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['withdrawal_method'].queryset = WithdrawalMethod.objects.filter(
                user=user, is_active=True
            )

class WithdrawalForm(forms.Form):
    """
    Расширенная форма для запроса на вывод средств
    """
    amount = forms.DecimalField(
        label=_('Amount'),
        min_value=100,
        max_value=100000,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter amount')
        })
    )
    
    withdrawal_method = forms.ModelChoiceField(
        label=_('Withdrawal Method'),
        queryset=WithdrawalMethod.objects.none(),
        empty_label=_('Select withdrawal method'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    comment = forms.CharField(
        label=_('Comment'),
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': _('Add any additional information'),
            'rows': 3
        })
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['withdrawal_method'].queryset = WithdrawalMethod.objects.filter(
                user=self.user,
                is_active=True
            )
    
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if self.user:
            wallet = self.user.wallet
            if amount > wallet.balance:
                raise forms.ValidationError(_("Insufficient funds in your wallet"))
        return amount

class TopUpForm(forms.Form):
    """
    Форма для пополнения кошелька с выбором способа оплаты
    """
    amount = forms.DecimalField(
        label=_('Amount'),
        min_value=100,
        max_value=100000,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter amount')
        })
    )
    
    payment_method = forms.ChoiceField(
        label=_('Payment Method'),
        choices=[
            ('yoomoney', _('YooMoney')),
            ('bank_card', _('Bank Card')),
            ('kaspi', _('Kaspi Bank')),
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )

class PaymentMethodForm(forms.ModelForm):
    """
    Форма для добавления метода вывода средств
    """
    class Meta:
        model = WithdrawalMethod
        fields = ['method_type', 'name', 'details', 'is_default']
        widgets = {
            'method_type': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Name for this method')}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['details'].widget = forms.HiddenInput()
        
        # Динамические поля в зависимости от типа метода
        self.bank_fields = {
            'bank_name': forms.CharField(
                label=_('Bank Name'),
                widget=forms.TextInput(attrs={'class': 'form-control'})
            ),
            'account_number': forms.CharField(
                label=_('Account Number'),
                widget=forms.TextInput(attrs={'class': 'form-control'})
            ),
            'account_holder': forms.CharField(
                label=_('Account Holder Name'),
                widget=forms.TextInput(attrs={'class': 'form-control'})
            )
        }
        
        self.yoomoney_fields = {
            'yoomoney_account': forms.CharField(
                label=_('YooMoney Account'),
                widget=forms.TextInput(attrs={'class': 'form-control'})
            )
        }
        
        self.kaspi_fields = {
            'phone_number': forms.CharField(
                label=_('Phone Number'),
                widget=forms.TextInput(attrs={'class': 'form-control'})
            ),
            'card_last_digits': forms.CharField(
                label=_('Last 4 digits of card'),
                widget=forms.TextInput(attrs={'class': 'form-control'})
            )
        }
        
        # Добавляем поля в форму в зависимости от типа метода
        if self.instance.pk and self.instance.method_type:
            method_type = self.instance.method_type
            if method_type == 'bank_transfer':
                for field_name, field in self.bank_fields.items():
                    self.fields[field_name] = field
                    if self.instance.details and field_name in self.instance.details:
                        field.initial = self.instance.details[field_name]
            elif method_type == 'yoomoney':
                for field_name, field in self.yoomoney_fields.items():
                    self.fields[field_name] = field
                    if self.instance.details and field_name in self.instance.details:
                        field.initial = self.instance.details[field_name]
            elif method_type == 'kaspi':
                for field_name, field in self.kaspi_fields.items():
                    self.fields[field_name] = field
                    if self.instance.details and field_name in self.instance.details:
                        field.initial = self.instance.details[field_name]
    
    def clean(self):
        cleaned_data = super().clean()
        method_type = cleaned_data.get('method_type')
        
        # Собираем детали в зависимости от типа метода
        details = {}
        if method_type == 'bank_transfer':
            for field_name in self.bank_fields:
                if field_name in cleaned_data:
                    details[field_name] = cleaned_data[field_name]
        elif method_type == 'yoomoney':
            for field_name in self.yoomoney_fields:
                if field_name in cleaned_data:
                    details[field_name] = cleaned_data[field_name]
        elif method_type == 'kaspi':
            for field_name in self.kaspi_fields:
                if field_name in cleaned_data:
                    details[field_name] = cleaned_data[field_name]
        
        cleaned_data['details'] = details
        return cleaned_data

class TransactionFilterForm(forms.Form):
    """
    Форма для фильтрации транзакций
    """
    type = forms.ChoiceField(
        label=_('Transaction Type'),
        choices=[('', _('All Types'))] + list(Transaction.TRANSACTION_TYPES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        label=_('Status'),
        choices=[('', _('All Statuses'))] + list(Transaction.STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_from = forms.DateField(
        label=_('From Date'),
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        label=_('To Date'),
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            self.add_error('date_to', _('End date should be greater than start date.'))
            
        return cleaned_data 

class WithdrawalMethodForm(forms.ModelForm):
    """
    Форма для добавления методов вывода средств
    """
    class Meta:
        model = WithdrawalMethod
        fields = ['method_type', 'name', 'is_default']
        widgets = {
            'method_type': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    # Динамические поля для разных типов вывода средств
    yoomoney_account = forms.CharField(
        label=_('YooMoney Account'),
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('YooMoney wallet number or email')}),
    )
    
    kaspi_account = forms.CharField(
        label=_('Kaspi Account'),
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Phone number linked to Kaspi account')}),
    )
    
    bank_name = forms.CharField(
        label=_('Bank Name'),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    
    bank_account = forms.CharField(
        label=_('Bank Account Number'),
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('IBAN or account number')}),
    )
    
    swift_code = forms.CharField(
        label=_('SWIFT/BIC Code'),
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    
    paypal_email = forms.EmailField(
        label=_('PayPal Email'),
        max_length=100,
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )
    
    crypto_type = forms.ChoiceField(
        label=_('Cryptocurrency'),
        choices=(
            ('btc', _('Bitcoin')),
            ('eth', _('Ethereum')),
            ('usdt', _('USDT')),
        ),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    
    crypto_address = forms.CharField(
        label=_('Wallet Address'),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Если это редактирование существующего метода, заполняем поля
        if self.instance.pk and self.instance.details:
            details = self.instance.details
            
            if self.instance.method_type == 'yoomoney':
                self.fields['yoomoney_account'].initial = details.get('account', '')
            
            elif self.instance.method_type == 'kaspi':
                self.fields['kaspi_account'].initial = details.get('account', '')
            
            elif self.instance.method_type == 'bank_transfer':
                self.fields['bank_name'].initial = details.get('bank_name', '')
                self.fields['bank_account'].initial = details.get('account', '')
                self.fields['swift_code'].initial = details.get('swift_code', '')
            
            elif self.instance.method_type == 'paypal':
                self.fields['paypal_email'].initial = details.get('email', '')
            
            elif self.instance.method_type == 'crypto':
                self.fields['crypto_type'].initial = details.get('crypto_type', 'btc')
                self.fields['crypto_address'].initial = details.get('address', '')
    
    def clean(self):
        cleaned_data = super().clean()
        method_type = cleaned_data.get('method_type')
        
        # Валидация данных в зависимости от типа вывода
        if method_type == 'yoomoney' and not cleaned_data.get('yoomoney_account'):
            self.add_error('yoomoney_account', _('YooMoney account is required'))
        
        elif method_type == 'kaspi' and not cleaned_data.get('kaspi_account'):
            self.add_error('kaspi_account', _('Kaspi account is required'))
        
        elif method_type == 'bank_transfer':
            if not cleaned_data.get('bank_name'):
                self.add_error('bank_name', _('Bank name is required'))
            if not cleaned_data.get('bank_account'):
                self.add_error('bank_account', _('Bank account number is required'))
        
        elif method_type == 'paypal' and not cleaned_data.get('paypal_email'):
            self.add_error('paypal_email', _('PayPal email is required'))
        
        elif method_type == 'crypto':
            if not cleaned_data.get('crypto_type'):
                self.add_error('crypto_type', _('Cryptocurrency type is required'))
            if not cleaned_data.get('crypto_address'):
                self.add_error('crypto_address', _('Wallet address is required'))
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        method_type = self.cleaned_data.get('method_type')
        
        # Создаем JSON с деталями в зависимости от типа вывода
        details = {}
        
        if method_type == 'yoomoney':
            details = {
                'account': self.cleaned_data.get('yoomoney_account'),
                'provider': 'YooMoney',
            }
        
        elif method_type == 'kaspi':
            details = {
                'account': self.cleaned_data.get('kaspi_account'),
                'provider': 'Kaspi Bank',
            }
        
        elif method_type == 'bank_transfer':
            details = {
                'bank_name': self.cleaned_data.get('bank_name'),
                'account': self.cleaned_data.get('bank_account'),
                'swift_code': self.cleaned_data.get('swift_code'),
            }
        
        elif method_type == 'paypal':
            details = {
                'email': self.cleaned_data.get('paypal_email'),
                'provider': 'PayPal',
            }
        
        elif method_type == 'crypto':
            details = {
                'crypto_type': self.cleaned_data.get('crypto_type'),
                'address': self.cleaned_data.get('crypto_address'),
                'provider': dict(self.fields['crypto_type'].choices).get(self.cleaned_data.get('crypto_type')),
            }
        
        instance.details = details
        
        if commit:
            instance.save()
        
        return instance 