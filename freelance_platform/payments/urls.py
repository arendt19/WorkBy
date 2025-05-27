from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Основные страницы
    path('wallet/', views.wallet_view, name='wallet'),
    path('transactions/', views.transaction_list_view, name='transaction_list'),
    path('transactions/<str:transaction_id>/', views.transaction_detail_view, name='transaction_detail'),
    
    # Операции с кошельком
    path('deposit/', views.deposit_view, name='deposit'),
    path('withdraw/', views.withdraw_view, name='withdraw'),
    
    # Демонстрационное пополнение баланса (только для разработки)
    # Демо-маршруты удалены в ходе очистки кода
    
    # Оплата вех
    path('milestone/<int:milestone_id>/pay/', views.pay_milestone_view, name='pay_milestone'),
    
    # Эскроу-платежи
    path('create-escrow/<int:milestone_id>/', views.create_escrow_payment, name='create_escrow'),
    path('fund-escrow/<str:escrow_id>/', views.fund_escrow, name='fund_escrow'),
    path('release-escrow/<str:escrow_id>/', views.release_escrow, name='release_escrow'),
    path('refund-escrow/<str:escrow_id>/', views.refund_escrow, name='refund_escrow'),
    path('dispute-escrow/<str:escrow_id>/', views.dispute_escrow, name='dispute_escrow'),
    
    # ЮMoney интеграция
    path('yoomoney/initiate/', views.yoomoney_initiate_payment, name='yoomoney_initiate_payment'),
    path('yoomoney/success/', views.yoomoney_success_callback, name='yoomoney_success_callback'),
    path('yoomoney/notification/', views.yoomoney_notification_callback, name='yoomoney_notification_callback'),
    
    # Управление методами вывода средств
    path('withdrawal-methods/', views.manage_withdrawal_methods, name='manage_withdrawal_methods'),
    path('withdrawal-methods/add/', views.add_withdrawal_method, name='add_withdrawal_method'),
    path('withdrawal-methods/edit/<int:pk>/', views.edit_withdrawal_method, name='edit_withdrawal_method'),
    path('withdrawal-methods/delete/<int:pk>/', views.delete_withdrawal_method, name='delete_withdrawal_method'),
    path('withdrawal-methods/set-default/<int:pk>/', views.set_default_withdrawal_method, name='set_default_withdrawal_method'),
    
    # История запросов на вывод средств
    path('withdrawal-history/', views.withdrawal_history, name='withdrawal_history'),
    
    # Webhook для YooMoney
    path('yoomoney-webhook/', views.yoomoney_webhook, name='yoomoney_webhook'),
] 