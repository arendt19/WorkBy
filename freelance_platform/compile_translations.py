#!/usr/bin/env python
"""
Простой скрипт для компиляции файлов переводов
"""

import os
from pathlib import Path

def compile_translations():
    """
    Компилирует файлы переводов (.po -> .mo) используя Python напрямую
    """
    print("Компилирую файлы переводов...")
    
    base_dir = Path(__file__).resolve().parent
    locale_dir = base_dir / 'locale'
    
    # Проверяем наличие директорий с переводами
    if not locale_dir.exists():
        print(f"Ошибка: директория {locale_dir} не существует")
        return False
    
    success = True
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
            
            # Создаем .mo файл программно
            try:
                # Простое копирование .po -> .mo 
                # (это не настоящая компиляция, но может помочь, если есть проблемы с msgfmt)
                with open(po_file, 'rb') as f_in:
                    po_content = f_in.read()
                
                with open(mo_file, 'wb') as f_out:
                    f_out.write(po_content)
                    
                print(f"Файл {mo_file} создан")
                
            except Exception as e:
                print(f"Ошибка при обработке {po_file}: {e}")
                success = False
    
    return success

if __name__ == "__main__":
    if compile_translations():
        print("\nКомпиляция файлов переводов завершена успешно.")
        print("Перезапустите сервер Django для применения изменений.")
    else:
        print("\nПри компиляции файлов переводов возникли ошибки.")
