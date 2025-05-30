import os
import django
import json
import sys
from datetime import datetime

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelance_core.settings')
django.setup()

# Импорт необходимых моделей
from django.contrib.auth import get_user_model
from accounts.models import FreelancerProfile, ClientProfile
from jobs.models import Category, Tag, Project
from modeltranslation.translator import translator

User = get_user_model()

def export_data():
    """Экспорт данных из SQLite"""
    data = {
        'users': [],
        'freelancer_profiles': [],
        'client_profiles': [],
        'categories': [],
        'tags': [],
        'projects': []
    }
    
    # Экспорт пользователей
    print("Экспорт пользователей...")
    for user in User.objects.all():
        user_data = {
            'username': user.username,
            'email': user.email,
            'password': user.password,  # Зашифрованный пароль
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_active': user.is_active,
            'is_superuser': user.is_superuser,
            'date_joined': str(user.date_joined),
            'user_type': getattr(user, 'user_type', None)
        }
        data['users'].append(user_data)
    
    # Экспорт профилей фрилансеров
    print("Экспорт профилей фрилансеров...")
    for profile in FreelancerProfile.objects.all():
        profile_data = {
            'user_username': profile.user.username,
            'bio': profile.bio,
            'specialization': profile.specialization,
            'experience_years': profile.experience_years,
            'hourly_rate': profile.hourly_rate,
            'skills': profile.skills,
            'education': profile.education if hasattr(profile, 'education') else None,
            'languages': profile.languages if hasattr(profile, 'languages') else None,
            'portfolio_website': profile.portfolio_website if hasattr(profile, 'portfolio_website') else None,
            'location': profile.location if hasattr(profile, 'location') else None,
            'is_available': profile.is_available
        }
        data['freelancer_profiles'].append(profile_data)
    
    # Экспорт профилей клиентов
    print("Экспорт профилей клиентов...")
    for profile in ClientProfile.objects.all():
        profile_data = {
            'user_username': profile.user.username,
            'company_name': profile.company_name,
            'company_website': profile.company_website if hasattr(profile, 'company_website') else None,
            'company_description': profile.company_description if hasattr(profile, 'company_description') else None,
            'industry': profile.industry if hasattr(profile, 'industry') else None,
            'company_size': profile.company_size if hasattr(profile, 'company_size') else None
        }
        data['client_profiles'].append(profile_data)
    
    # Экспорт категорий с переводами
    print("Экспорт категорий...")
    for category in Category.objects.all():
        category_data = {
            'name': category.name,
            'slug': category.slug,
            'description': category.description,
            'icon': category.icon,
        }
        
        # Добавление переводов
        for lang in ['ru', 'kk']:
            name_field = f'name_{lang}'
            desc_field = f'description_{lang}'
            if hasattr(category, name_field):
                category_data[name_field] = getattr(category, name_field)
            if hasattr(category, desc_field):
                category_data[desc_field] = getattr(category, desc_field)
        
        data['categories'].append(category_data)
    
    # Экспорт тегов с переводами
    print("Экспорт тегов...")
    for tag in Tag.objects.all():
        tag_data = {
            'name': tag.name,
            'slug': tag.slug,
        }
        
        # Добавление переводов
        for lang in ['ru', 'kk']:
            name_field = f'name_{lang}'
            if hasattr(tag, name_field):
                tag_data[name_field] = getattr(tag, name_field)
        
        data['tags'].append(tag_data)
    
    # Экспорт проектов
    print("Экспорт проектов...")
    for project in Project.objects.all():
        project_data = {
            'title': project.title,
            'slug': project.slug,
            'client_username': project.client.username,
            'category_name': project.category.name,
            'description': project.description,
            'requirements': project.requirements,
            'budget_min': project.budget_min,
            'budget_max': project.budget_max,
            'deadline': str(project.deadline) if project.deadline else None,
            'status': project.status,
            'created_at': str(project.created_at),
            'tags': [tag.name for tag in project.tags.all()]
        }
        
        # Добавление переводов
        for lang in ['ru', 'kk']:
            title_field = f'title_{lang}'
            desc_field = f'description_{lang}'
            req_field = f'requirements_{lang}'
            
            if hasattr(project, title_field):
                project_data[title_field] = getattr(project, title_field)
            if hasattr(project, desc_field):
                project_data[desc_field] = getattr(project, desc_field)
            if hasattr(project, req_field):
                project_data[req_field] = getattr(project, req_field)
        
        data['projects'].append(project_data)
    
    # Сохранение данных в JSON файл
    print("Сохранение данных в JSON файл...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"db_export_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"Данные успешно экспортированы в файл {filename}")
    return filename

if __name__ == "__main__":
    export_data()
