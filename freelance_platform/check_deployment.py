#!/usr/bin/env python
"""
Скрипт для проверки настроек перед деплоем
"""
import os
import sys
import subprocess

def check_dependencies():
    """Проверяет установку зависимостей"""
    required_packages = [
        'django', 'python-dotenv', 'channels', 
        'daphne', 'gunicorn', 'whitenoise'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} установлен")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} не установлен")
    
    if missing_packages:
        print("\nОтсутствуют следующие пакеты:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nУстановите их с помощью:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_env_vars():
    """Проверяет необходимые переменные окружения"""
    try:
        # Сначала пробуем загрузить .env файл, если он есть
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print("✅ Переменные окружения загружены из .env файла")
        except ImportError:
            print("⚠️  python-dotenv не установлен, .env файл не загружен")
        
        # Критические настройки
        critical_vars = ['SECRET_KEY', 'DEBUG']
        optional_vars = ['DATABASE_URL', 'ALLOWED_HOSTS', 'CSRF_TRUSTED_ORIGINS']
        
        missing_critical = []
        missing_optional = []
        
        for var in critical_vars:
            if os.environ.get(var):
                print(f"✅ {var} установлен")
            else:
                missing_critical.append(var)
                print(f"❌ {var} не установлен")
        
        for var in optional_vars:
            if os.environ.get(var):
                print(f"✅ {var} установлен")
            else:
                missing_optional.append(var)
                print(f"⚠️  {var} не установлен")
        
        if missing_critical:
            print("\nОтсутствуют критические переменные окружения:")
            for var in missing_critical:
                print(f"  - {var}")
            return False
        
        if missing_optional:
            print("\nОтсутствуют опциональные переменные окружения:")
            for var in missing_optional:
                print(f"  - {var}")
        
        return True
    
    except Exception as e:
        print(f"Ошибка при проверке переменных окружения: {e}")
        return False

def check_django_settings():
    """Проверяет настройки Django"""
    try:
        # Установка переменной окружения для настроек Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelance_core.settings')
        
        # Импорт необходимых для проверки модулей
        import django
        django.setup()
        
        from django.conf import settings
        
        # Проверка критических настроек
        if settings.DEBUG:
            print("⚠️  DEBUG=True - не рекомендуется для продакшена")
        else:
            print("✅ DEBUG=False - хорошо для продакшена")
        
        if 'sslserver' in settings.INSTALLED_APPS and not settings.DEBUG:
            print("⚠️  'sslserver' находится в INSTALLED_APPS в режиме продакшена")
        else:
            print("✅ Настройки INSTALLED_APPS корректны")
        
        # Проверяем настройки ALLOWED_HOSTS
        if settings.ALLOWED_HOSTS == ['*'] and not settings.DEBUG:
            print("⚠️  ALLOWED_HOSTS=['*'] в режиме продакшена - рекомендуется указать конкретные хосты")
        elif len(settings.ALLOWED_HOSTS) > 0 and settings.ALLOWED_HOSTS != ['*']:
            print(f"✅ ALLOWED_HOSTS установлены: {settings.ALLOWED_HOSTS}")
        
        return True
    
    except Exception as e:
        print(f"Ошибка при проверке настроек Django: {e}")
        return False

def main():
    """Основная функция проверки"""
    print("=== Проверка зависимостей ===")
    deps_ok = check_dependencies()
    
    print("\n=== Проверка переменных окружения ===")
    env_ok = check_env_vars()
    
    print("\n=== Проверка настроек Django ===")
    settings_ok = check_django_settings()
    
    print("\n=== Результаты проверки ===")
    if deps_ok and env_ok and settings_ok:
        print("✅ Все проверки пройдены. Можно выполнять деплой.")
        return 0
    else:
        print("❌ Есть проблемы, которые нужно исправить перед деплоем.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 