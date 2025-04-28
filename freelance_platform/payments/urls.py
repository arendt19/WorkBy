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
    
    # Оплата вех
    path('milestone/<int:milestone_id>/pay/', views.pay_milestone_view, name='pay_milestone'),
    
    # ЮMoney интеграция
    path('yoomoney/initiate/', views.yoomoney_initiate_payment, name='yoomoney_initiate_payment'),
    path('yoomoney/success/', views.yoomoney_success_callback, name='yoomoney_success_callback'),
    path('yoomoney/notification/', views.yoomoney_notification_callback, name='yoomoney_notification_callback'),
] 