#!/usr/bin/env python
"""
Скрипт для удаления тестовых и демонстрационных сообщений из базы данных.
"""

import os
import django

# Настройка окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelance_core.settings')
django.setup()

from chat.models import Message, Conversation
from django.db.models import Q

def clean_test_messages():
    """Удаление всех тестовых сообщений из базы данных."""
    print("Начинаю очистку тестовых сообщений...")
    
    # Ищем и удаляем тестовые сообщения по ключевым словам
    test_keywords = [
        'автоматическое тестовое сообщение',
        'тестовое сообщение',
        'отправите сообщение',
        'появится здесь',
        'проверить отображение',
        'test message'
    ]
    
    # Создаем запрос для поиска сообщений по ключевым словам
    q_objects = Q()
    for keyword in test_keywords:
        q_objects |= Q(content__icontains=keyword)
    
    # Подсчитываем и удаляем найденные сообщения
    messages_to_delete = Message.objects.filter(q_objects)
    count = messages_to_delete.count()
    
    if count > 0:
        messages_to_delete.delete()
        print(f"Удалено {count} тестовых сообщений.")
    else:
        print("Тестовых сообщений не найдено.")
    
    # Очищаем демо-транзакции и другие тестовые данные
    print("Очистка завершена.")

if __name__ == "__main__":
    clean_test_messages()
