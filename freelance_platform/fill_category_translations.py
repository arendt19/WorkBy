#!/usr/bin/env python
import os
import django
import sys

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelance_core.settings')
django.setup()

from jobs.models import Category
from googletrans import Translator

def translate_categories():
    """
    Автоматически заполняет поля name_ru и name_kk для всех категорий, 
    используя переводчик Google, если эти поля не заполнены.
    """
    translator = Translator()
    categories = Category.objects.all()
    updated = 0
    
    # Словарь с предопределенными переводами для общих категорий
    predefined_translations = {
        'Audio & Video': {
            'ru': 'Аудио и видео',
            'kk': 'Аудио және видео'
        },
        'Copywriting & Content': {
            'ru': 'Копирайтинг и контент',
            'kk': 'Копирайтинг және контент'
        },
        'Data Science & Analytics': {
            'ru': 'Наука о данных и аналитика',
            'kk': 'Деректер ғылымы және аналитика'
        },
        'Design & UX/UI': {
            'ru': 'Дизайн и UX/UI',
            'kk': 'Дизайн және UX/UI'
        },
        'Digital Marketing': {
            'ru': 'Цифровой маркетинг',
            'kk': 'Цифрлық маркетинг'
        },
        'Finance & Accounting': {
            'ru': 'Финансы и бухгалтерия',
            'kk': 'Қаржы және бухгалтерлік есеп'
        },
        'Legal Services': {
            'ru': 'Юридические услуги',
            'kk': 'Заңдық қызметтер'
        },
        'Mobile Development': {
            'ru': 'Мобильная разработка',
            'kk': 'Мобильді әзірлеу'
        },
        'Web Development': {
            'ru': 'Веб-разработка',
            'kk': 'Веб әзірлеу'
        }
    }
    
    print("Обновление переводов категорий...")
    
    for category in categories:
        source_name = category.name_en if category.name_en else category.name
        name_changed = False
        
        # Проверяем, есть ли предопределенный перевод
        if source_name in predefined_translations:
            # Заполняем русский перевод, если он пустой
            if not category.name_ru:
                category.name_ru = predefined_translations[source_name]['ru']
                name_changed = True
                
            # Заполняем казахский перевод, если он пустой
            if not category.name_kk:
                category.name_kk = predefined_translations[source_name]['kk']
                name_changed = True
        else:
            # Используем Google Translate для не предопределенных категорий
            try:
                # Заполняем русский перевод, если он пустой
                if not category.name_ru:
                    ru_translation = translator.translate(source_name, src='en', dest='ru').text
                    category.name_ru = ru_translation
                    name_changed = True
                    
                # Заполняем казахский перевод, если он пустой
                if not category.name_kk:
                    kk_translation = translator.translate(source_name, src='en', dest='kk').text
                    category.name_kk = kk_translation
                    name_changed = True
            except Exception as e:
                print(f"Ошибка перевода '{source_name}': {e}")
        
        # Сохраняем изменения, если были сделаны переводы
        if name_changed:
            category.save()
            updated += 1
            print(f"Обновлена категория: {source_name} -> ru: {category.name_ru}, kk: {category.name_kk}")
    
    print(f"Обновлено {updated} из {categories.count()} категорий.")

if __name__ == "__main__":
    translate_categories()
    print("Готово! Теперь категории имеют переводы на русский и казахский языки.")
    print("Пожалуйста, перезапустите сервер Django для применения изменений.")
