#!/usr/bin/env python
"""
Скрипт для исправления проблем с переводами в проекте WorkBy
"""

import os
import sys
import re
import glob
import subprocess
from pathlib import Path

def compile_translations():
    """
    Компилирует файлы переводов (.po -> .mo) без использования Django команд
    """
    print("Компилирую файлы переводов...")
    
    base_dir = Path(__file__).resolve().parent
    locale_dir = base_dir / 'locale'
    
    # Проверяем наличие директорий с переводами
    if not locale_dir.exists():
        print(f"Ошибка: директория {locale_dir} не существует")
        return False
    
    # Обходим все языковые директории
    for lang_dir in locale_dir.iterdir():
        if not lang_dir.is_dir():
            continue
            
        lc_messages_dir = lang_dir / 'LC_MESSAGES'
        if not lc_messages_dir.exists() or not lc_messages_dir.is_dir():
            continue
            
        # Ищем .po файлы
        for po_file in lc_messages_dir.glob('*.po'):
            mo_file = po_file.with_suffix('.mo')
            
            # Компиляция через Python без использования msgfmt
            try:
                with open(po_file, 'rb') as f:
                    po_content = f.read()
                    
                # Попробуем использовать polib для компиляции если есть
                try:
                    import polib
                    print(f"Компилирую {po_file} с использованием polib...")
                    po = polib.pofile(str(po_file))
                    po.save_as_mofile(str(mo_file))
                    print(f"Файл {mo_file} успешно создан")
                    
                # Если polib не установлен, вызовем подпроцесс с msgfmt
                except ImportError:
                    print(f"polib не найден, пробую msgfmt для {po_file}...")
                    try:
                        result = subprocess.run(
                            ['msgfmt', '-o', str(mo_file), str(po_file)], 
                            capture_output=True, 
                            text=True
                        )
                        if result.returncode == 0:
                            print(f"Файл {mo_file} успешно создан через msgfmt")
                        else:
                            print(f"Ошибка при выполнении msgfmt: {result.stderr}")
                            
                            # Крайний случай: копируем .po как .mo
                            print(f"Аварийная копия {po_file} -> {mo_file}...")
                            with open(mo_file, 'wb') as mf:
                                mf.write(po_content)
                    except FileNotFoundError:
                        print("Команда msgfmt не найдена в системе")
                        # Крайний случай: копируем .po как .mo
                        print(f"Аварийная копия {po_file} -> {mo_file}...")
                        with open(mo_file, 'wb') as mf:
                            mf.write(po_content)
            except Exception as e:
                print(f"Ошибка при обработке {po_file}: {e}")
                continue
    
    return True

def check_templates_translations():
    """
    Проверяет шаблоны на наличие текстов без перевода
    """
    print("\nПроверяю шаблоны на наличие непереведенных строк...")
    
    base_dir = Path(__file__).resolve().parent
    templates_dir = base_dir / 'templates'
    
    html_files = list(templates_dir.glob('**/*.html'))
    potential_issues = []
    
    # Шаблоны строк, которые должны быть обернуты в теги перевода
    words_to_check = [
        r'Find\s+the\s+perfect', r'Browse\s+projects', r'Search', r'How\s+It\s+Works',
        r'Register', r'Find', r'Work', r'Get\s+Paid', r'Collaborate', r'Secure\s+payments',
        r'Learn\s+More', r'projects', r'View\s+Profile', r'View\s+All', r'Latest\s+Projects',
        r'Top\s+Rated'
    ]
    
    for html_file in html_files:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Проверяем наличие основных тегов перевода
        has_load_i18n = {% load i18n %}" in content
        if not has_load_i18n:
            potential_issues.append(f"Файл {html_file.relative_to(base_dir)} не содержит тега {% load i18n %}")
        
        # Ищем необернутые строки (вне тегов trans)
        for line_number, line in enumerate(content.split('\n'), 1):
            # Пропускаем комментарии и уже обернутые строки
            if line.strip().startswith('<!--') or "{% trans" in line:
                continue
                
            for word in words_to_check:
                matches = re.findall(rf'\b{word}\b', line, re.IGNORECASE)
                if matches:
                    potential_issues.append(f"Файл {html_file.relative_to(base_dir)}:{line_number} - возможно непереведенный текст: '{line.strip()}'")
    
    if potential_issues:
        print("\nВозможные проблемы с переводами в шаблонах:")
        for issue in potential_issues:
            print(f"- {issue}")
    else:
        print("Не найдено явных проблем с переводами в шаблонах")

def fix_category_translations():
    """
    Исправляет проблему с переводами категорий напрямую в базе данных
    """
    try:
        import django
        from django.conf import settings
        
        # Настраиваем Django
        sys.path.append('.')
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelance_platform.settings')
        django.setup()
        
        from jobs.models import Category
        
        print("\nПроверяю и исправляю переводы категорий...")
        
        categories = Category.objects.all()
        for category in categories:
            print(f"Категория: {category.name}")
            
            if not category.name_en:
                print(f"  - Добавляю английский перевод: '{category.name}'")
                category.name_en = category.name
                
            if not category.name_ru:
                # Словарь для базовых переводов
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
                
                if category.name in en_to_ru:
                    print(f"  - Добавляю русский перевод: '{en_to_ru[category.name]}'")
                    category.name_ru = en_to_ru[category.name]
                
            if not category.name_kk:
                # Словарь для базовых переводов
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
                
                if category.name in en_to_kk:
                    print(f"  - Добавляю казахский перевод: '{en_to_kk[category.name]}'")
                    category.name_kk = en_to_kk[category.name]
            
            category.save()
        
        print("Переводы категорий обновлены")
        
    except Exception as e:
        print(f"Ошибка при обновлении переводов категорий: {e}")
        return False
    
    return True

def fix_template_category_references():
    """
    Исправляет шаблоны, где категории сравниваются по имени вместо слага
    """
    print("\nИсправляю шаблоны с некорректными ссылками на категории...")
    
    base_dir = Path(__file__).resolve().parent
    templates_dir = base_dir / 'templates'
    
    # Исправляем home.html, где используется сравнение с английскими названиями
    home_html = templates_dir / 'jobs' / 'home.html'
    if home_html.exists():
        with open(home_html, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Заменяем сравнения по имени на сравнения по слагу
        patterns = [
            (r"{% if category.name == 'Design & Creative' %}", "{% if category.slug == 'design-creative' %}"),
            (r"{% elif category.name == 'Web Development' %}", "{% elif category.slug == 'web-development' %}"),
            (r"{% elif category.name == 'Mobile Development' %}", "{% elif category.slug == 'mobile-development' %}"),
            (r"{% elif category.name == 'Writing & Translation' %}", "{% elif category.slug == 'writing-translation' %}"),
            (r"{% elif category.name == 'Marketing' %}", "{% elif category.slug == 'marketing' %}"),
            (r"{% elif category.name == 'Finance & Accounting' %}", "{% elif category.slug == 'finance-accounting' %}"),
            (r"{% elif category.name == 'Legal Services' %}", "{% elif category.slug == 'legal-services' %}"),
            (r"{% elif category.name == 'Virtual Assistance' %}", "{% elif category.slug == 'virtual-assistance' %}"),
        ]
        
        for old, new in patterns:
            content = content.replace(old, new)
        
        # Сохраняем исправленный файл
        with open(home_html, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"Файл {home_html.relative_to(base_dir)} обновлен")

def main():
    print("=== Начинаю исправление проблем с переводами ===")
    
    # Шаг 1: Компилируем файлы переводов
    if not compile_translations():
        print("Не удалось скомпилировать файлы переводов")
    
    # Шаг 2: Проверяем и исправляем переводы категорий
    fix_category_translations()
    
    # Шаг 3: Исправляем шаблоны с некорректными ссылками
    fix_template_category_references()
    
    # Шаг 4: Проверяем шаблоны на непереведенные строки
    check_templates_translations()
    
    print("\n=== Исправление проблем с переводами завершено ===")
    print("Перезапустите сервер Django для применения изменений")

if __name__ == "__main__":
    main()
