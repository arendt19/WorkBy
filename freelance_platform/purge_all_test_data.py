#!/usr/bin/env python
"""
Скрипт для полного удаления всех тестовых данных из базы данных.
"""

import os
import django
import sys

# Настройка окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelance_core.settings')
django.setup()

from chat.models import Message, Conversation
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

def purge_all_test_data():
    """Радикальная очистка всех тестовых данных."""
    print("ВНИМАНИЕ: Начинаю радикальную очистку всех тестовых данных...")
    
    # 1. Удаляем ВСЕ сообщения из системы
    message_count = Message.objects.all().count()
    Message.objects.all().delete()
    print(f"✓ Удалено ВСЕ {message_count} сообщений из системы")
    
    # 2. Удаляем только сообщения с "Error sending message"
    # error_messages = Message.objects.filter(content__icontains="Error sending message")
    # error_count = error_messages.count()
    # error_messages.delete()
    # print(f"✓ Удалено {error_count} сообщений с ошибками")
    
    print("✓ Очистка успешно завершена!")
    
if __name__ == "__main__":
    confirm = input("Это действие удалит ВСЕ сообщения в системе. Продолжить? (y/n): ")
    if confirm.lower() == 'y':
        purge_all_test_data()
    else:
        print("Операция отменена.")
