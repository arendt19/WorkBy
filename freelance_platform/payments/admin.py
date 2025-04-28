from django.contrib import admin
from .models import Transaction, Wallet

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'amount', 'transaction_type', 'status', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('transaction_id', 'user__username', 'description')
    readonly_fields = ('transaction_id', 'created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('transaction_id', 'user', 'amount', 'transaction_type', 'status')
        }),
        ('Дополнительная информация', {
            'fields': ('description', 'reference_id', '_meta_data')
        }),
        ('Связи', {
            'fields': ('contract', 'milestone', 'related_transaction')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at') 