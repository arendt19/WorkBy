import os
import sys
import django
import random
from datetime import datetime, timedelta

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelance_core.settings')
django.setup()

# Импорт моделей Django после настройки
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.utils import timezone
from django.db import connection
from django.core.management import call_command

from accounts.models import FreelancerProfile, ClientProfile
from jobs.models import Category, Tag, Project, Proposal

User = get_user_model()

def setup_database():
    # Применяем миграции
    print("Применяем миграции...")
    call_command('migrate')
    
    # Создаем суперпользователя
    print("Создаем суперпользователя...")
    if not User.objects.filter(username='arendt').exists():
        User.objects.create_superuser('arendt', 'admin@example.com', 'password123')
        print("Суперпользователь 'arendt' создан")
    else:
        print("Суперпользователь 'arendt' уже существует")
    
    # Создаем тестовых пользователей
    print("Создаем тестовых пользователей...")
    
    # Создаем фрилансера
    if not User.objects.filter(username='freelancer2').exists():
        freelancer = User.objects.create_user(
            username='freelancer2',
            email='freelancer2@example.com',
            password='password123',
            first_name='Иван',
            last_name='Фрилансеров'
        )
        freelancer.user_type = 'freelancer'
        freelancer.save()
        
        # Создаем профиль фрилансера
        freelancer_profile = FreelancerProfile.objects.create(
            user=freelancer,
            bio="Опытный разработчик с более чем 5-летним стажем работы.",
            specialization="Веб-разработчик Full Stack",
            experience_years=5,
            hourly_rate=3000,
            skills="Python, Django, JavaScript, React, HTML, CSS",
            education="Высшее техническое, МГТУ",
            languages="Русский, Английский, Казахский",
            portfolio_website="https://example.com/portfolio",
            location="Алматы, Казахстан",
            is_available=True
        )
        print("Пользователь 'freelancer2' создан")
    else:
        print("Пользователь 'freelancer2' уже существует")
    
    # Создаем клиента
    if not User.objects.filter(username='client2').exists():
        client = User.objects.create_user(
            username='client2',
            email='client2@example.com',
            password='password123',
            first_name='Петр',
            last_name='Заказчиков'
        )
        client.user_type = 'client'
        client.save()
        
        # Создаем профиль клиента
        client_profile = ClientProfile.objects.create(
            user=client,
            company_name="ООО Технологии Будущего",
            company_website="https://example.com/company",
            company_description="Компания, специализирующаяся на инновационных технологических решениях.",
            industry="IT и технологии",
            company_size="10-50 сотрудников"
        )
        print("Пользователь 'client2' создан")
    else:
        print("Пользователь 'client2' уже существует")
    
    # Создаем категории с переводами
    print("Создаем категории с переводами...")
    categories_data = [
        {
            'name': 'Web Development',
            'name_ru': 'Веб-разработка',
            'name_kk': 'Веб-дамыту',
            'description': 'Design and development of websites and web applications',
            'description_ru': 'Дизайн и разработка веб-сайтов и веб-приложений',
            'description_kk': 'Веб-сайттар мен веб-қосымшаларды жобалау және әзірлеу',
            'icon': 'fa-laptop-code'
        },
        {
            'name': 'Mobile App Development',
            'name_ru': 'Разработка мобильных приложений',
            'name_kk': 'Мобильді қосымшаларды жасау',
            'description': 'Design and development of mobile applications for iOS and Android',
            'description_ru': 'Дизайн и разработка мобильных приложений для iOS и Android',
            'description_kk': 'iOS және Android үшін мобильді қосымшаларды жобалау және әзірлеу',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'Graphic Design',
            'name_ru': 'Графический дизайн',
            'name_kk': 'Графикалық дизайн',
            'description': 'Creation of visual content to communicate messages',
            'description_ru': 'Создание визуального контента для передачи сообщений',
            'description_kk': 'Хабарламаларды жеткізу үшін визуалды мазмұн жасау',
            'icon': 'fa-palette'
        },
        {
            'name': 'Content Writing',
            'name_ru': 'Копирайтинг',
            'name_kk': 'Мазмұн жазу',
            'description': 'Writing, editing, and publishing content',
            'description_ru': 'Написание, редактирование и публикация контента',
            'description_kk': 'Мазмұнды жазу, өңдеу және жариялау',
            'icon': 'fa-pen-fancy'
        },
        {
            'name': 'Digital Marketing',
            'name_ru': 'Цифровой маркетинг',
            'name_kk': 'Сандық маркетинг',
            'description': 'Marketing of products and services using digital technologies',
            'description_ru': 'Маркетинг продуктов и услуг с использованием цифровых технологий',
            'description_kk': 'Сандық технологияларды қолдана отырып, өнімдер мен қызметтердің маркетингі',
            'icon': 'fa-chart-line'
        },
    ]
    
    for cat_data in categories_data:
        cat, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'description': cat_data['description'],
                'icon': cat_data['icon']
            }
        )
        
        # Добавляем переводы
        if hasattr(cat, 'name_ru'):
            cat.name_ru = cat_data['name_ru']
        if hasattr(cat, 'name_kk'):
            cat.name_kk = cat_data['name_kk']
        if hasattr(cat, 'description_ru'):
            cat.description_ru = cat_data['description_ru']
        if hasattr(cat, 'description_kk'):
            cat.description_kk = cat_data['description_kk']
        cat.save()
        
        if created:
            print(f"Категория '{cat.name}' создана")
        else:
            print(f"Категория '{cat.name}' обновлена")
    
    # Создаем теги с переводами
    print("Создаем теги с переводами...")
    tags_data = [
        {'name': 'HTML', 'name_ru': 'HTML', 'name_kk': 'HTML'},
        {'name': 'CSS', 'name_ru': 'CSS', 'name_kk': 'CSS'},
        {'name': 'JavaScript', 'name_ru': 'JavaScript', 'name_kk': 'JavaScript'},
        {'name': 'Python', 'name_ru': 'Python', 'name_kk': 'Python'},
        {'name': 'Django', 'name_ru': 'Django', 'name_kk': 'Django'},
        {'name': 'React', 'name_ru': 'React', 'name_kk': 'React'},
        {'name': 'Angular', 'name_ru': 'Angular', 'name_kk': 'Angular'},
        {'name': 'Node.js', 'name_ru': 'Node.js', 'name_kk': 'Node.js'},
        {'name': 'iOS', 'name_ru': 'iOS', 'name_kk': 'iOS'},
        {'name': 'Android', 'name_ru': 'Android', 'name_kk': 'Android'},
    ]
    
    for tag_data in tags_data:
        tag, created = Tag.objects.get_or_create(
            name=tag_data['name']
        )
        
        # Добавляем переводы
        if hasattr(tag, 'name_ru'):
            tag.name_ru = tag_data['name_ru']
        if hasattr(tag, 'name_kk'):
            tag.name_kk = tag_data['name_kk']
        tag.save()
        
        if created:
            print(f"Тег '{tag.name}' создан")
        else:
            print(f"Тег '{tag.name}' обновлен")
    
    # Создаем тестовые проекты
    print("Создаем тестовые проекты...")
    
    # Получаем клиента и категории
    client = User.objects.get(username='client2')
    categories = list(Category.objects.all())
    tags = list(Tag.objects.all())
    
    # Создаем 5 тестовых проектов
    project_titles = [
        "Разработка корпоративного веб-сайта",
        "Мобильное приложение для доставки еды",
        "Редизайн логотипа компании",
        "Написание контента для блога",
        "SEO-оптимизация интернет-магазина"
    ]
    
    for i, title in enumerate(project_titles):
        # Выбираем случайную категорию
        category = random.choice(categories)
        
        # Выбираем случайные теги (от 2 до 4)
        selected_tags = random.sample(tags, random.randint(2, min(4, len(tags))))
        
        # Создаем проект
        project, created = Project.objects.get_or_create(
            title=title,
            defaults={
                'client': client,
                'category': category,
                'description': f"Подробное описание проекта '{title}'. Мы ищем опытного специалиста для выполнения этой работы.",
                'requirements': "Требования: опыт работы от 2 лет, знание современных технологий, ответственность и соблюдение сроков.",
                'budget_min': random.randint(10000, 50000),
                'budget_max': random.randint(50000, 150000),
                'deadline': timezone.now() + timedelta(days=random.randint(7, 30)),
                'status': random.choice(['open', 'in_progress', 'completed'])
            }
        )
        
        # Добавляем теги к проекту
        for tag in selected_tags:
            project.tags.add(tag)
        
        if created:
            print(f"Проект '{project.title}' создан")
        else:
            print(f"Проект '{project.title}' уже существует")
    
    print("\nБаза данных успешно настроена!")

if __name__ == "__main__":
    setup_database()
