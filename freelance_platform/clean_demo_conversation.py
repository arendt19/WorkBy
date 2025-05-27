#!/usr/bin/env python
"""
Скрипт для удаления всех сообщений из демонстрационного разговора,
который отображается на скриншоте.
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

def clean_demo_conversations():
    """Очистка демонстрационных и тестовых разговоров с автоматическими сообщениями."""
    print("Начинаю очистку демонстрационных разговоров...")
    
    # Найдем пользователя по имени пользователя
    username = "Фрилансер2"
    try:
        freelancer = User.objects.filter(Q(username__icontains=username) | 
                                        Q(first_name__icontains=username) | 
                                        Q(last_name__icontains=username)).first()
        if not freelancer:
            print(f"Пользователь '{username}' не найден.")
            return
            
        print(f"Найден пользователь: {freelancer.username} (ID: {freelancer.id})")
        
        # Найдем все разговоры, в которых участвует этот пользователь
        conversations = Conversation.objects.filter(participants=freelancer)
        
        if conversations.count() == 0:
            print(f"Разговоры с пользователем '{username}' не найдены.")
            return
            
        print(f"Найдено {conversations.count()} разговоров с пользователем '{username}'")
        
        # Для каждого разговора удалим все сообщения
        total_messages = 0
        for conversation in conversations:
            messages_count = Message.objects.filter(conversation=conversation).count()
            Message.objects.filter(conversation=conversation).delete()
            print(f"Удалено {messages_count} сообщений из разговора {conversation.id}")
            total_messages += messages_count
            
        print(f"Всего удалено {total_messages} сообщений из {conversations.count()} разговоров")
        
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        
if __name__ == "__main__":
    clean_demo_conversations()
