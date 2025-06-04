from django.urls import path
from . import views
from . import support_views
from . import test_views

app_name = 'chat'

urlpatterns = [
    # Страницы
    path('', views.inbox_view, name='inbox'),
    path('conversation/<int:conversation_id>/', views.conversation_detail_view, name='conversation_detail'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('start-conversation/<int:user_id>/', views.start_conversation_view, name='start_conversation'),
    path('support/', views.support_chat_view, name='support_chat'),  # Страница чата с ботом

    # API
    path('api/send_message/<int:pk>/', views.api_send_message_view, name='api_send_message'),
    path('api/unread_count/', views.api_unread_count_view, name='api_unread_count'),
    path('api/mark_notification_read/<int:pk>/', views.mark_notification_read_view, name='api_mark_notification_read'),
    path('api/check_messages/<int:pk>/', views.api_check_messages_view, name='api_check_messages'),
    path('api/mark_messages_read/<int:pk>/', views.api_mark_messages_read_view, name='api_mark_messages_read'),
    
    # Бот поддержки
    path('support-bot/', views.support_bot_view, name='support_bot'),
    
    # Тестовая страница
    path('test-button/', test_views.test_button_view, name='test_button'),
] 