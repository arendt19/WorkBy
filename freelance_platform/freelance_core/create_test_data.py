# coding=utf-8
import random
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from django.core.files.uploadedfile import SimpleUploadedFile
import os
from pathlib import Path

from jobs.models import Category, Tag, Project, Proposal, Contract, Milestone
from accounts.models import UserProfile, Skill, Education, Experience, Review
from payments.models import Wallet, Transaction

User = get_user_model()

# Получаем путь к тестовым изображениям
BASE_DIR = Path(__file__).resolve().parent.parent
TEST_IMAGES_DIR = os.path.join(BASE_DIR, 'static/test_images')

# Обработчик загрузки тестовых данных
@transaction.atomic
def create_test_data():
    print("Создание тестовых данных...")
    
    # Создаем суперпользователя, если его нет
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@workby.io',
            password='admin'
        )
        
        # Создаем профиль для админа
        UserProfile.objects.create(
            user=admin,
            first_name='Admin',
            last_name='User',
            bio='Администратор платформы',
            phone_number='+7777777777',
        )
        
        # Создаем кошелек для админа
        Wallet.objects.create(
            user=admin,
            balance=50000.00
        )
    
    # Создаем клиентов
    clients = []
    
    if not User.objects.filter(username='client1').exists():
        client1 = User.objects.create_user(
            username='client1',
            email='client1@example.com',
            password='workby123'
        )
        
        UserProfile.objects.create(
            user=client1,
            first_name='Алексей',
            last_name='Клиентов',
            bio='Владелец агентства цифрового маркетинга',
            is_freelancer=False,
            phone_number='+7777111111',
        )
        
        Wallet.objects.create(
            user=client1,
            balance=100000.00
        )
        
        clients.append(client1)
    
    if not User.objects.filter(username='client2').exists():
        client2 = User.objects.create_user(
            username='client2',
            email='client2@example.com',
            password='workby123'
        )
        
        UserProfile.objects.create(
            user=client2,
            first_name='Елена',
            last_name='Заказчикова',
            bio='Руководитель IT-отдела',
            is_freelancer=False,
            phone_number='+7777222222',
        )
        
        Wallet.objects.create(
            user=client2,
            balance=75000.00
        )
        
        clients.append(client2)
    
    # Создаем фрилансеров
    freelancers = []
    
    if not User.objects.filter(username='freelancer1').exists():
        freelancer1 = User.objects.create_user(
            username='freelancer1',
            email='freelancer1@example.com',
            password='workby123'
        )
        
        UserProfile.objects.create(
            user=freelancer1,
            first_name='Иван',
            last_name='Фрилансеров',
            bio='Опытный веб-разработчик с 5-летним опытом',
            is_freelancer=True,
            hourly_rate=2000,
            phone_number='+7777333333',
        )
        
        Wallet.objects.create(
            user=freelancer1,
            balance=25000.00
        )
        
        freelancers.append(freelancer1)
    
    if not User.objects.filter(username='freelancer2').exists():
        freelancer2 = User.objects.create_user(
            username='freelancer2',
            email='freelancer2@example.com',
            password='workby123'
        )
        
        UserProfile.objects.create(
            user=freelancer2,
            first_name='Мария',
            last_name='Дизайнерова',
            bio='UX/UI дизайнер с портфолио мирового уровня',
            is_freelancer=True,
            hourly_rate=2500,
            phone_number='+7777444444',
        )
        
        Wallet.objects.create(
            user=freelancer2,
            balance=30000.00
        )
        
        freelancers.append(freelancer2)
    
    # Создаем категории и теги
    categories = []
    for name in ['Веб-разработка', 'Мобильная разработка', 'Дизайн', 
                'Контент и копирайтинг', 'Маркетинг']:
        if not Category.objects.filter(name=name).exists():
            category = Category.objects.create(name=name)
            categories.append(category)
    
    tags = []
    for name in ['Python', 'JavaScript', 'Django', 'React', 'Angular', 'Vue.js', 
                'HTML', 'CSS', 'SQL', 'NoSQL']:
        if not Tag.objects.filter(name=name).exists():
            tag = Tag.objects.create(name=name)
            tags.append(tag)
    
    # Создаем проекты
    if not Project.objects.exists():
        for i in range(5):
            project = Project.objects.create(
                title=f'Тестовый проект {i+1}',
                description=f'Описание тестового проекта {i+1}. Это пример проекта для демонстрации функционала платформы.',
                client=random.choice(clients),
                category=random.choice(categories),
                budget_type=random.choice(['fixed', 'hourly']),
                budget_min=5000,
                budget_max=15000,
                deadline=timezone.now() + timezone.timedelta(days=random.randint(10, 30)),
                status='open',
                is_remote=True
            )
            
            # Добавляем случайные теги
            project_tags = random.sample(list(tags), random.randint(2, 5))
            project.tags.add(*project_tags)
            
            # Создаем предложения для проекта
            for freelancer in freelancers:
                if random.choice([True, False]):
                    Proposal.objects.create(
                        freelancer=freelancer,
                        project=project,
                        cover_letter=f'Предлагаю свои услуги для выполнения проекта {project.title}.',
                        bid_amount=random.randint(int(project.budget_min), int(project.budget_max)),
                        delivery_time=random.randint(5, 20),
                        status=random.choice(['pending', 'accepted', 'rejected'])
                    )
    
    # Создаем контракты и вехи
    if not Contract.objects.exists():
        projects = list(Project.objects.filter(status='open')[:2])
        
        for i, project in enumerate(projects):
            freelancer = freelancers[i % len(freelancers)]
            
            # Создаем предложение, если его нет
            proposal, created = Proposal.objects.get_or_create(
                freelancer=freelancer,
                project=project,
                defaults={
                    'cover_letter': f'Предлагаю свои услуги для выполнения проекта {project.title}.',
                    'bid_amount': random.randint(int(project.budget_min), int(project.budget_max)),
                    'delivery_time': random.randint(5, 20),
                    'status': 'accepted'
                }
            )
            
            # Создаем контракт
            contract = Contract.objects.create(
                title=f'Контракт для {project.title}',
                description=f'Условия выполнения проекта {project.title}',
                client=project.client,
                freelancer=freelancer,
                project=project,
                proposal=proposal,
                amount=proposal.bid_amount,
                deadline=timezone.now() + timezone.timedelta(days=proposal.delivery_time),
                status='active'
            )
            
            # Обновляем статус проекта и предложения
            project.status = 'in_progress'
            project.save()
            
            proposal.status = 'accepted'
            proposal.save()
            
            # Создаем вехи для контракта
            milestones_count = random.randint(2, 4)
            amount_per_milestone = contract.amount / milestones_count
            
            for j in range(milestones_count):
                milestone_status = 'completed' if j == 0 else 'pending' if j == 1 else 'in_progress'
                payment_status = 'paid' if milestone_status == 'completed' else 'escrow' if milestone_status == 'in_progress' else 'not_paid'
                
                Milestone.objects.create(
                    contract=contract,
                    title=f'Веха {j+1} - {project.title}',
                    description=f'Описание вехи {j+1} для проекта {project.title}',
                    amount=amount_per_milestone,
                    due_date=timezone.now() + timezone.timedelta(days=(j+1)*7),
                    status=milestone_status,
                    payment_status=payment_status
                )
    
    print("Тестовые данные созданы успешно!")
    return True

