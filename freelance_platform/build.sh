#!/bin/bash
set -e

echo "============================="
echo "WorkBy Platform Build Script"
echo "============================="

# Проверка на наличие незакоммиченных конфликтов Git
echo "Checking for Git conflict markers..."
python scripts/check_for_git_conflicts.py
if [ $? -ne 0 ]; then
    echo "ERROR: Git conflict markers found. Please resolve conflicts before building."
    exit 1
fi

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

# Сборка статических файлов
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Компиляция переводов
echo "Compiling translations..."
python manage.py compilemessages

# Миграции базы данных
echo "Running database migrations..."
python manage.py migrate

echo "============================="
echo "Build completed successfully!"
echo "=============================" 