from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Transaction

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
        min_value=100,
        max_value=100000,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter amount')
        })
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if self.user:
            wallet = self.user.wallet
            if amount > wallet.balance:
                raise forms.ValidationError(_("Insufficient funds in your wallet"))
        return amount

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