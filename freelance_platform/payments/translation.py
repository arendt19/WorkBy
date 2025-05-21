from modeltranslation.translator import register, TranslationOptions
from .models import Transaction

@register(Transaction)
class TransactionTranslationOptions(TranslationOptions):
    fields = ('description',) 