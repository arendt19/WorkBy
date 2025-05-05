#!/bin/bash
set -e

# Вывод информации о среде
echo "=== Информация о среде ==="
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"
echo "Directory: $(pwd)"
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

# Подготовка статических файлов
echo "=== Сбор статических файлов ==="
python manage.py collectstatic --noinput

# Применение миграций
echo "=== Применение миграций ==="
python manage.py migrate

echo "=== Сборка завершена успешно ===" 