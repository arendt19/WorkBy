#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для удаления дублирующихся записей в файлах локализации .po
"""

import re
import os
import sys

def remove_duplicates_from_po_file(filename):
    """
    Удаляет дублирующиеся msgid/msgstr пары из файла .po
    """
    print(f"Обработка файла: {filename}")
    
    # Чтение файла
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Регулярное выражение для поиска записей msgid/msgstr
    pattern = r'(msgid "(.+?)"\nmsgstr "(.+?)")'
    
    # Найдем все совпадения
    matches = re.findall(pattern, content, re.DOTALL)
    
    # Словарь для хранения уникальных записей
    unique_entries = {}
    duplicates = []
    
    # Для каждого совпадения проверим, существует ли уже такой msgid
    for full_match, msgid, msgstr in matches:
        if msgid in unique_entries:
            duplicates.append((msgid, full_match))
        else:
            unique_entries[msgid] = full_match
    
    # Если есть дубликаты, удалим их из файла
    if duplicates:
        print(f"Найдены дубликаты: {len(duplicates)}")
        
        for msgid, full_match in duplicates:
            print(f"Удаление дубликата для: '{msgid}'")
            # Заменяем полное совпадение на пустую строку
            content = content.replace(full_match, '')
        
        # Сохраняем изменения
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Дубликаты удалены из файла: {filename}")
        return True
    else:
        print(f"Дубликаты не найдены в файле: {filename}")
        return False

def main():
    """
    Основная функция
    """
    # Пути к файлам локализации
    locale_paths = [
        'locale/ru/LC_MESSAGES/django.po',
        'locale/kk/LC_MESSAGES/django.po'
    ]
    
    changes_made = False
    
    # Обработка каждого файла
    for path in locale_paths:
        if os.path.exists(path):
            if remove_duplicates_from_po_file(path):
                changes_made = True
        else:
            print(f"Файл не найден: {path}")
    
    if changes_made:
        print("\nВыполните команду для компиляции переводов:")
        print("python manage.py compilemessages")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
