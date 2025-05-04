#!/usr/bin/env python
"""
Скрипт для автоматического исправления настроек SSL в проекте.
"""
import os
import sys
import re


def fix_ssl_settings(settings_file='freelance_core/settings.py'):
    """
    Исправляет настройки SSL в файле settings.py
    """
    if not os.path.exists(settings_file):
        print(f"Файл {settings_file} не найден")
        return False
    
    with open(settings_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем, добавлены ли уже наши изменения
    if 'IS_LOCAL = os.environ.get' in content:
        print("Настройки уже исправлены")
        return True
    
    # Добавляем переменную IS_LOCAL
    content = re.sub(
        r'(DEBUG\s*=\s*os\.environ\.get.*)',
        r'\1\n\n# Определяем, запущен ли сервер на локальной машине\nIS_LOCAL = os.environ.get(\'SERVER_ENV\', \'local\') == \'local\'',
        content
    )
    
    # Исправляем настройки прокси-заголовка
    content = re.sub(
        r'(# Настройки для локальной разработки с HTTPS\n)SECURE_PROXY_SSL_HEADER',
        r'\1# Настройка прокси-заголовка для определения протокола (для production)\nif not IS_LOCAL:\n    SECURE_PROXY_SSL_HEADER',
        content
    )
    
    # Исправляем настройки безопасности
    content = re.sub(
        r'(# Производственные настройки безопасности\n)if not DEBUG:',
        r'\1if not DEBUG and not IS_LOCAL:',
        content
    )
    
    # Добавляем настройки для разработки
    content = re.sub(
        r'(    X_FRAME_OPTIONS = \'DENY\')',
        r'\1\nelse:\n    # Для локальной разработки отключаем редирект на HTTPS\n    SECURE_SSL_REDIRECT = False\n    SESSION_COOKIE_SECURE = False\n    CSRF_COOKIE_SECURE = False',
        content
    )
    
    # Сохраняем изменения
    with open(settings_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Настройки SSL в {settings_file} успешно исправлены")
    return True


if __name__ == "__main__":
    if fix_ssl_settings():
        print("Теперь вы можете запустить сервер с помощью:")
        print("python run_ssl_server.py")
        print("или:")
        print("python manage.py runserver")
    else:
        print("Не удалось исправить настройки SSL")
        sys.exit(1) 