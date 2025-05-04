#!/usr/bin/env python
"""
Скрипт для запуска Django с поддержкой HTTPS
через django-sslserver с автоматической генерацией сертификатов.
"""
import os
import sys
import subprocess

def ensure_ssl_certificates():
    """Проверяет наличие SSL-сертификатов или генерирует их"""
    ssl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ssl')
    
    if not os.path.exists(ssl_dir):
        os.makedirs(ssl_dir)
    
    cert_file = os.path.join(ssl_dir, 'sslserver.crt')
    key_file = os.path.join(ssl_dir, 'sslserver.key')
    
    if not (os.path.exists(cert_file) and os.path.exists(key_file)):
        print("SSL-сертификаты не найдены. Генерирую новые...")
        
        # Запускаем скрипт генерации сертификатов
        generate_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'generate_ssl_cert.py')
        if os.path.exists(generate_script):
            subprocess.run([sys.executable, generate_script], check=True)
        else:
            print("Скрипт generate_ssl_cert.py не найден. Создаю сертификаты вручную...")
            openssl_command = [
                'openssl', 'req', '-x509', '-nodes',
                '-days', '365',
                '-newkey', 'rsa:2048',
                '-keyout', key_file,
                '-out', cert_file,
                '-subj', '/CN=localhost/O=WorkBy/C=KZ'
            ]
            try:
                subprocess.run(openssl_command, check=True)
                print("Сертификаты успешно созданы.")
            except subprocess.CalledProcessError as e:
                print(f"Ошибка при генерации сертификатов: {e}")
                print("Запускаю сервер без SSL...")
                return False
    
    # Устанавливаем переменные окружения для sslserver
    os.environ['SSLSERVER_CERTIFICATE'] = cert_file
    os.environ['SSLSERVER_KEY'] = key_file
    return True

if __name__ == "__main__":
    # Проверяем/генерируем SSL-сертификаты
    has_ssl = ensure_ssl_certificates()
    
    # Устанавливаем переменные окружения
    os.environ.setdefault("SERVER_ENV", "local")
    os.environ.setdefault("DJANGO_DEBUG", "True")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "freelance_core.settings")
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Запускаем сервер с правильными параметрами
    if has_ssl:
        print("Запускаю сервер с SSL на порту 8000...")
        execute_from_command_line(["manage.py", "runsslserver", "--addrport=0.0.0.0:8000"] + sys.argv[1:])
    else:
        print("Запускаю обычный сервер без SSL...")
        execute_from_command_line(["manage.py", "runserver", "0.0.0.0:8000"] + sys.argv[1:]) 