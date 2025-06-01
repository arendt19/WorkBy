#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import django
from django.utils import translation
from django.conf import settings

# Настройка окружения Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelance_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import FreelancerProfile, ClientProfile

User = get_user_model()

def update_test_accounts():
    """
    Обновляет тестовые аккаунты, заполняя их реалистичной информацией.
    """
    print("Обновление тестовых аккаунтов...")
    
    # Словарь с новыми данными для пользователей
    users_data = {
        'arendt': {
            'new_username': 'alexey_petrov',
            'email': 'alex.petrov@workby.net',
            'first_name': 'Алексей',
            'last_name': 'Петров',
            'user_type': 'client',
            'bio': 'Владелец IT-компании с опытом более 10 лет. Специализируемся на разработке веб-приложений и мобильных решений для бизнеса.',
            'skills': '',
            'phone_number': '+77771234567',
            'company_name': 'TechSolutions'
        },
        'freelancer2': {
            'new_username': 'marina_design',
            'email': 'marina.design@workby.net',
            'first_name': 'Марина',
            'last_name': 'Иванова',
            'user_type': 'freelancer',
            'bio': 'Профессиональный веб-дизайнер с опытом более 5 лет. Специализируюсь на создании современных адаптивных интерфейсов и брендинге.',
            'skills': 'UI/UX дизайн, Figma, Adobe Photoshop, Иллюстрация, Веб-дизайн, Брендинг, HTML/CSS',
            'phone_number': '+77079876543',
            'hourly_rate': 25
        },
        'client2': {
            'new_username': 'startup_kz',
            'email': 'info@startup-kz.com',
            'first_name': 'Ержан',
            'last_name': 'Нурланов',
            'user_type': 'client',
            'bio': 'Руководитель стартапа в сфере e-commerce. Ищем талантливых специалистов для развития нашего онлайн-маркетплейса.',
            'skills': '',
            'phone_number': '+77015551234',
            'company_name': 'KazMarket'
        }
    }
    
    # Обновляем данные пользователей
    for old_username, data in users_data.items():
        try:
            user = User.objects.get(username=old_username)
            print(f"Обновление пользователя {old_username} -> {data['new_username']}")
            
            # Сохраняем старый user_type
            user_type = user.user_type
            
            # Обновляем основные поля
            user.username = data['new_username']
            user.email = data['email']
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.user_type = data['user_type']
            user.bio = data['bio']
            user.skills = data['skills']
            user.phone_number = data['phone_number']
            
            if user.user_type == 'client':
                user.company_name = data['company_name']
            elif user.user_type == 'freelancer' and 'hourly_rate' in data:
                user.hourly_rate = data['hourly_rate']
                
            user.save()
            
            # Обновляем или создаем профили
            if user.user_type == 'freelancer':
                freelancer_profile, created = FreelancerProfile.objects.get_or_create(user=user)
                freelancer_profile.portfolio_website = f"https://{data['new_username']}.portfolio.com"
                freelancer_profile.is_available = True
                freelancer_profile.experience_years = 5
                freelancer_profile.education = "Высшее образование в сфере дизайна, Университет искусств и дизайна"
                freelancer_profile.certifications = "Adobe Certified Expert, UX Design Institute Certificate"
                freelancer_profile.specialization = "UI/UX дизайн и брендинг"
                freelancer_profile.languages = "Русский, Английский, Казахский"
                freelancer_profile.save()
                print(f"  Обновлен профиль фрилансера для {data['new_username']}")
                
            elif user.user_type == 'client':
                client_profile, created = ClientProfile.objects.get_or_create(user=user)
                client_profile.company_website = f"https://www.{data['company_name'].lower().replace(' ', '')}.kz"
                client_profile.industry = "IT и разработка" if data['new_username'] == 'alexey_petrov' else "Электронная коммерция"
                client_profile.company_size = 15 if data['new_username'] == 'alexey_petrov' else 8
                client_profile.save()
                print(f"  Обновлен профиль клиента для {data['new_username']}")
                
            # Если изменился тип пользователя, создаем соответствующий профиль
            if user_type != user.user_type:
                print(f"  Тип пользователя изменился с {user_type} на {user.user_type}")
                
        except User.DoesNotExist:
            print(f"Пользователь {old_username} не найден")

def fix_project_translations():
    """
    Исправляет проблему с переводами описаний проектов.
    """
    print("\nИсправление переводов описаний проектов...")
    
    from jobs.models import Project
    
    projects = Project.objects.all()
    
    for project in projects:
        # Создаем или обновляем переводы заголовка и описания проекта
        
        # Английская версия (оригинал)
        title_en = project.title
        description_en = project.description
        
        # Русская версия
        title_ru = None
        description_ru = None
        
        # Казахская версия
        title_kk = None
        description_kk = None
        
        # В зависимости от типа проекта, создаем разные переводы
        if "разработка" in project.title.lower() or "веб-сайт" in project.title.lower():
            title_ru = project.title
            description_ru = project.description
            
            # Английский перевод
            title_en = title_ru.replace("Разработка", "Development of").replace("веб-сайта", "website").replace("для", "for")
            description_en = "Professional development of a modern website with responsive design and intuitive interface. The project includes front-end and back-end development, database integration, and content management system."
            
            # Казахский перевод
            title_kk = title_ru.replace("Разработка", "Әзірлеу").replace("веб-сайта", "веб-сайтын").replace("для", "үшін")
            description_kk = "Заманауи веб-сайтты бейімделгіш дизайнмен және интуитивті интерфейспен кәсіби әзірлеу. Жоба front-end және back-end әзірлеуді, дерекқор интеграциясын және контентті басқару жүйесін қамтиды."
            
        elif "дизайн" in project.title.lower():
            title_ru = project.title
            description_ru = project.description
            
            # Английский перевод
            title_en = title_ru.replace("Дизайн", "Design of").replace("логотипа", "logo").replace("для", "for")
            description_en = "Creative design of a modern and memorable logo that reflects the company's values and mission. The project includes several concept options, revisions, and delivery in various formats for different uses."
            
            # Казахский перевод
            title_kk = title_ru.replace("Дизайн", "Дизайн").replace("логотипа", "логотипін").replace("для", "үшін")
            description_kk = "Компанияның құндылықтары мен миссиясын көрсететін заманауи және есте қаларлық логотиптің креативті дизайны. Жоба бірнеше тұжырымдама нұсқаларын, түзетулерді және әртүрлі пайдалану үшін әртүрлі форматтарда жеткізуді қамтиды."
            
        else:
            # По умолчанию для других типов проектов
            title_ru = project.title
            description_ru = project.description
            
            # Базовые переводы
            title_en = "Project: " + title_ru
            description_en = "This is an English description of the project."
            
            title_kk = "Жоба: " + title_ru
            description_kk = "Бұл жобаның қазақша сипаттамасы."
        
        # Сохраняем разные языковые версии
        project.title = title_en  # По умолчанию на английском
        project.description = description_en
        
        # Сохраняем русскую версию
        translation.activate('ru')
        project.title = title_ru
        project.description = description_ru
        
        # Сохраняем казахскую версию
        translation.activate('kk')
        project.title = title_kk
        project.description = description_kk
        
        # Возвращаемся к английскому для продолжения
        translation.activate('en')
        
        project.save()
        print(f"Обновлены переводы для проекта: {project.title}")
    
    print("Переводы проектов успешно обновлены!")

def modify_username_validation():
    """
    Заменяет ошибку валидации на ненавязчивую рекомендацию.
    """
    print("\nИзменение сообщений валидации профиля...")
    
    # Тут мы должны найти соответствующие файлы и изменить в них сообщения об ошибках
    # на более дружелюбные рекомендации.
    
    # Для этого требуется изменить соответствующие шаблоны или формы, 
    # но без более конкретной информации о структуре проекта
    # невозможно точно определить, где эти сообщения находятся.
    
    print("Примечание: Для полного изменения сообщений валидации требуется ручное редактирование форм и шаблонов.")

if __name__ == "__main__":
    print("Начинаем обновление тестовых данных и исправление проблем...")
    update_test_accounts()
    fix_project_translations()
    modify_username_validation()
    print("Обновление завершено!")
