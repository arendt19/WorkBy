from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Message

class MessageForm(forms.ModelForm):
    """
    Форма для отправки сообщения
    """
    content = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'rows': 3, 
            'placeholder': _('Type your message...'),
            'class': 'form-control'
        }),
        error_messages={
            'required': _('You cannot send an empty message'),
        }
    )
    
    class Meta:
        model = Message
        fields = ['content'] 