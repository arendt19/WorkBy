#!/bin/bash
set -e

# Вывод информации о среде
echo "=== Информация о среде ==="
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"
echo "Directory: $(pwd)"
echo "Содержимое директории:"
ls -la
echo "============================="

# Установка зависимостей
echo "=== Установка зависимостей ==="
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install django-sslserver python-dotenv --no-cache-dir

# Проверка установленных пакетов
echo "=== Проверка установленных пакетов ==="
pip list | grep sslserver
pip list | grep dotenv

# Проверка настроек Django
echo "=== Проверка настроек Django ==="
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelance_core.settings'); import django; django.setup(); from django.conf import settings; print('DEBUG =', settings.DEBUG); print('INSTALLED_APPS =', settings.INSTALLED_APPS)"

# Проверка структуры проекта
echo "=== Структура проекта ==="
find . -type f -name "settings.py" | xargs ls -la
echo "Содержимое settings.py:"
find . -type f -name "settings.py" | xargs cat | grep -A 10 -B 10 "sslserver"

# Подготовка статических файлов
echo "=== Сбор статических файлов ==="
python manage.py collectstatic --noinput

# Применение миграций
echo "=== Применение миграций ==="
python manage.py migrate

echo "=== Сборка завершена успешно ===" 