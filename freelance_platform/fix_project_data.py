import os
import django
import re

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelance_core.settings')
django.setup()

from django.db.models import Q
from jobs.models import Project, Category, Tag

# 1. Исправление названий проектов (удаление префикса "Project: ")
projects_with_prefix = Project.objects.filter(title__startswith="Project:")
fixed_titles_count = 0

for project in projects_with_prefix:
    old_title = project.title
    # Удаляем префикс "Project: " и оставляем только название
    new_title = re.sub(r'^Project:\s*', '', old_title)
    
    # Если название пустое после удаления префикса, пропускаем
    if not new_title.strip():
        continue
    
    project.title = new_title
    project.save()
    print(f"Исправлено название: '{old_title}' -> '{new_title}'")
    fixed_titles_count += 1

print(f"\nИсправлено названий проектов: {fixed_titles_count}")

# 2. Исправление несоответствия между названиями проектов и категориями
category_keyword_mapping = {
    'веб': 'Web Development',
    'сайт': 'Web Development',
    'web': 'Web Development',
    'вебсайт': 'Web Development',
    'website': 'Web Development',
    'лендинг': 'Web Development',
    'landing': 'Web Development',
    
    'мобильн': 'Mobile Development',
    'android': 'Mobile Development',
    'ios': 'Mobile Development',
    'app': 'Mobile Development',
    'приложени': 'Mobile Development',
    
    'дизайн': 'Design & UI/UX',
    'логотип': 'Design & UI/UX',
    'ui': 'Design & UI/UX',
    'ux': 'Design & UI/UX',
    'интерфейс': 'Design & UI/UX',
    'макет': 'Design & UI/UX',
    'баннер': 'Design & UI/UX',
    'design': 'Design & UI/UX',
    'logo': 'Design & UI/UX',
    
    'статья': 'Content & Copywriting',
    'текст': 'Content & Copywriting',
    'контент': 'Content & Copywriting',
    'копирайт': 'Content & Copywriting',
    'blog': 'Content & Copywriting',
    'блог': 'Content & Copywriting',
    'content': 'Content & Copywriting',
    'writing': 'Content & Copywriting',
    
    'перевод': 'Translation & Localization',
    'локализ': 'Translation & Localization',
    'translation': 'Translation & Localization',
    'localization': 'Translation & Localization',
    
    'маркетинг': 'Digital Marketing',
    'marketing': 'Digital Marketing',
    'smm': 'Digital Marketing',
    'реклам': 'Digital Marketing',
    'promotion': 'Digital Marketing',
    'продвижени': 'Digital Marketing',
    
    'seo': 'SEO & SEM',
    'поисков': 'SEO & SEM',
    'search': 'SEO & SEM',
    'оптимизац': 'SEO & SEM',
    'optimization': 'SEO & SEM',
    
    'видео': 'Audio & Video Production',
    'аудио': 'Audio & Video Production',
    'video': 'Audio & Video Production',
    'audio': 'Audio & Video Production',
    'podcast': 'Audio & Video Production',
    'монтаж': 'Audio & Video Production',
    
    'данны': 'Data Science & Analytics',
    'аналитик': 'Data Science & Analytics',
    'data': 'Data Science & Analytics',
    'analytics': 'Data Science & Analytics',
    'machine learning': 'Data Science & Analytics',
    'ml': 'Data Science & Analytics',
    'ai': 'Data Science & Analytics',
    
    'финанс': 'Finance & Accounting',
    'бухгалт': 'Finance & Accounting',
    'accounting': 'Finance & Accounting',
    'finance': 'Finance & Accounting',
    'бюджет': 'Finance & Accounting',
    
    'юридич': 'Legal Services',
    'legal': 'Legal Services',
    'договор': 'Legal Services',
    'контракт': 'Legal Services',
    'contract': 'Legal Services',
    
    'ассистент': 'Virtual Assistance & Admin Support',
    'assistant': 'Virtual Assistance & Admin Support',
    'поддержк': 'Virtual Assistance & Admin Support',
    'support': 'Virtual Assistance & Admin Support',
    'админ': 'Virtual Assistance & Admin Support',
    'admin': 'Virtual Assistance & Admin Support',
}

# Получаем словарь категорий для быстрого доступа
categories = {}
for category in Category.objects.all():
    categories[category.name_en] = category

fixed_categories_count = 0

# Проходим по всем проектам
for project in Project.objects.all():
    title_lower = project.title.lower()
    description_lower = project.description.lower() if project.description else ""
    
    # Определяем наиболее подходящую категорию по названию и описанию
    best_category = None
    max_matches = 0
    
    for keyword, category_name in category_keyword_mapping.items():
        # Считаем сколько совпадений с ключевыми словами в названии (вес x3)
        title_matches = title_lower.count(keyword.lower()) * 3
        # Считаем сколько совпадений с ключевыми словами в описании (вес x1)
        desc_matches = description_lower.count(keyword.lower())
        total_matches = title_matches + desc_matches
        
        if total_matches > max_matches:
            max_matches = total_matches
            best_category = category_name
    
    # Если нашли подходящую категорию и она отличается от текущей
    if best_category and best_category in categories and project.category != categories[best_category]:
        old_category = project.category.name_en if project.category else "None"
        project.category = categories[best_category]
        project.save()
        print(f"Исправлена категория для '{project.title}': {old_category} -> {best_category}")
        fixed_categories_count += 1

print(f"Исправлено категорий проектов: {fixed_categories_count}")

# Общая статистика
total_projects = Project.objects.count()
print(f"\nОбщая статистика:")
print(f"Всего проектов: {total_projects}")
print(f"Процент исправленных названий: {fixed_titles_count/total_projects*100:.1f}%")
print(f"Процент исправленных категорий: {fixed_categories_count/total_projects*100:.1f}%")
