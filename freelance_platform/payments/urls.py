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
    path('demo-add-balance/', views.demo_add_balance_view, name='demo_add_balance'),
    path('demo-add-balance/<int:amount>/', views.demo_add_balance_view, name='demo_add_balance_amount'),
    
    # Оплата вех
    path('milestone/<int:milestone_id>/pay/', views.pay_milestone_view, name='pay_milestone'),
    
    # Эскроу-платежи
    path('milestone/<int:milestone_id>/create-escrow/', views.create_escrow_payment, name='create_escrow'),
    path('escrow/<str:escrow_id>/fund/', views.fund_escrow, name='fund_escrow'),
    path('escrow/<str:escrow_id>/release/', views.release_escrow, name='release_escrow'),
    path('escrow/<str:escrow_id>/refund/', views.refund_escrow, name='refund_escrow'),
    path('escrow/<str:escrow_id>/dispute/', views.dispute_escrow, name='dispute_escrow'),
    
    # ЮMoney интеграция
    path('yoomoney/initiate/', views.yoomoney_initiate_payment, name='yoomoney_initiate_payment'),
    path('yoomoney/success/', views.yoomoney_success_callback, name='yoomoney_success_callback'),
    path('yoomoney/notification/', views.yoomoney_notification_callback, name='yoomoney_notification_callback'),
] 