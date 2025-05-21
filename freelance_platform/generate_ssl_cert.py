#!/usr/bin/env python
"""
Скрипт для генерации самоподписанных SSL-сертификатов
для django-sslserver.
"""
import os
import subprocess
import sys

def generate_ssl_cert():
    """
    Генерирует самоподписанный SSL-сертификат для локальной разработки.
    """
    ssl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ssl')
    
    # Создаем директорию, если она не существует
    if not os.path.exists(ssl_dir):
        os.makedirs(ssl_dir)
    
    cert_file = os.path.join(ssl_dir, 'sslserver.crt')
    key_file = os.path.join(ssl_dir, 'sslserver.key')
    
    # Проверяем, существуют ли уже сертификаты
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print(f"Сертификаты уже существуют в {ssl_dir}")
        print("Если вы хотите создать новые сертификаты, удалите существующие файлы и запустите скрипт снова.")
        return
    
    print("Генерирую самоподписанный SSL-сертификат для localhost...")
    
    # Общая команда для Windows и Unix-подобных систем
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
        print(f"Сертификаты успешно сгенерированы в директории {ssl_dir}")
        print(f"Сертификат: {cert_file}")
        print(f"Ключ: {key_file}")
        
        # Установка переменных окружения для django-sslserver
        os.environ['SSLSERVER_CERTIFICATE'] = cert_file
        os.environ['SSLSERVER_KEY'] = key_file
        
        print("\nДля запуска сервера с SSL используйте команду:")
        print("python manage.py runsslserver --addrport=0.0.0.0:8000")
        
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при генерации сертификатов: {e}")
        print("Убедитесь, что OpenSSL установлен и доступен в PATH.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(generate_ssl_cert()) 