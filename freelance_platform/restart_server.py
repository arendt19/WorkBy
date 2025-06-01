"""
Скрипт для очистки кэша переводов и перезапуска сервера Django
"""
import os
import shutil
import sys
import subprocess
from pathlib import Path

def clear_cache():
    """Очищает кэш переводов и Python-кэш"""
    print("Очистка кэша переводов...")
    
    # Удаляем все .pyc файлы
    base_dir = Path(__file__).resolve().parent
    for pyc_file in base_dir.glob('**/*.pyc'):
        try:
            os.remove(pyc_file)
            print(f"Удален файл: {pyc_file}")
        except Exception as e:
            print(f"Не удалось удалить {pyc_file}: {e}")
    
    # Удаляем директории __pycache__
    for pycache_dir in base_dir.glob('**/__pycache__'):
        try:
            shutil.rmtree(pycache_dir)
            print(f"Удалена директория: {pycache_dir}")
        except Exception as e:
            print(f"Не удалось удалить {pycache_dir}: {e}")
    
    # Очищаем кэш сессий Django
    try:
        from django.core.management import call_command
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelance_core.settings')
        django.setup()
        call_command('clearsessions')
        print("Сессии Django очищены")
    except Exception as e:
        print(f"Не удалось очистить сессии Django: {e}")
    
    print("Кэш очищен")

def update_category_translations():
    """Обновляет переводы категорий в базе данных"""
    try:
        print("\nОбновление переводов категорий в базе данных...")
        
        import django
        from django.conf import settings
        
        # Настраиваем Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelance_core.settings')
        django.setup()
        
        # Импортируем модель Category
        from jobs.models import Category
        
        # Словари для переводов
        en_to_ru = {
            'Web Development': 'Веб-разработка',
            'Mobile Development': 'Мобильная разработка',
            'Design & Creative': 'Дизайн и творчество',
            'Writing & Translation': 'Написание и перевод',
            'Marketing': 'Маркетинг',
            'Finance & Accounting': 'Финансы и бухгалтерия',
            'Legal Services': 'Юридические услуги',
            'Virtual Assistance': 'Виртуальная помощь',
            'IT & Networking': 'ИТ и сети',
            'Data Science': 'Наука о данных',
            'Engineering': 'Инженерия',
            'Other': 'Другое'
        }
        
        en_to_kk = {
            'Web Development': 'Веб-әзірлеу',
            'Mobile Development': 'Мобильді әзірлеу',
            'Design & Creative': 'Дизайн және шығармашылық',
            'Writing & Translation': 'Жазу және аудару',
            'Marketing': 'Маркетинг',
            'Finance & Accounting': 'Қаржы және бухгалтерия',
            'Legal Services': 'Заңгерлік қызметтер',
            'Virtual Assistance': 'Виртуалды көмек',
            'IT & Networking': 'IT және желілер',
            'Data Science': 'Деректер ғылымы',
            'Engineering': 'Инженерия',
            'Other': 'Басқа'
        }
        
        # Обновляем переводы для всех категорий
        categories = Category.objects.all()
        for category in categories:
            print(f"Категория: {category.name}")
            
            # Устанавливаем английский перевод
            if not category.name_en:
                category.name_en = category.name
                print(f"  - Добавлен английский перевод: {category.name_en}")
            
            # Устанавливаем русский перевод
            if category.name in en_to_ru and not category.name_ru:
                category.name_ru = en_to_ru[category.name]
                print(f"  - Добавлен русский перевод: {category.name_ru}")
            
            # Устанавливаем казахский перевод
            if category.name in en_to_kk and not category.name_kk:
                category.name_kk = en_to_kk[category.name]
                print(f"  - Добавлен казахский перевод: {category.name_kk}")
            
            category.save()
        
        print("Переводы категорий обновлены")
    except Exception as e:
        print(f"Ошибка при обновлении переводов категорий: {e}")

def restart_server():
    """Перезапускает сервер разработки Django"""
    print("\nПерезапуск сервера Django...")
    
    # Получаем PID текущего процесса
    current_pid = os.getpid()
    
    # Создаем bat-файл для перезапуска сервера
    restart_bat = Path(__file__).resolve().parent / "restart_django.bat"
    with open(restart_bat, 'w') as f:
        f.write('@echo off\n')
        f.write('echo Ожидаем завершения текущего процесса...\n')
        f.write(f'taskkill /F /PID {current_pid} /T > nul 2>&1\n')
        f.write('cd /d "%~dp0"\n')
        f.write('echo Запускаем сервер Django...\n')
        f.write('python manage.py runserver\n')
    
    # Запускаем bat-файл в новом окне
    subprocess.Popen(['start', 'cmd', '/k', str(restart_bat)], shell=True)
    
    print("Инициирован перезапуск сервера.")

if __name__ == "__main__":
    clear_cache()
    update_category_translations()
    restart_server()
