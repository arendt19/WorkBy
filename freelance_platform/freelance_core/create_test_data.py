import os
import django
import random
from datetime import timedelta
from django.utils import timezone

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelance_core.settings')
django.setup()

# Импорт моделей
from accounts.models import User, FreelancerProfile, ClientProfile, PortfolioProject, Review
from jobs.models import Category, Tag, Project, Proposal, Contract, Milestone
from payments.models import Wallet, Transaction

# Создание категорий
def create_categories():
    categories = [
        {"name": "Веб-разработка", "slug": "web-development"},
        {"name": "Мобильная разработка", "slug": "mobile-development"},
        {"name": "Дизайн", "slug": "design"},
        {"name": "Контент и копирайтинг", "slug": "content"},
        {"name": "Маркетинг", "slug": "marketing"},
        {"name": "Перевод", "slug": "translation"},
        {"name": "SEO и SMM", "slug": "seo-smm"},
        {"name": "Аудио и видео", "slug": "audio-video"},
    ]
    
    for cat in categories:
        Category.objects.get_or_create(name=cat["name"], slug=cat["slug"])
    
    return Category.objects.all()

# Создание тегов
def create_tags():
    tags = [
        "Python", "JavaScript", "Django", "React", "Angular", "Vue.js", "HTML", "CSS", 
        "SQL", "NoSQL", "Swift", "Kotlin", "Java", "Flutter", "PHP", "Laravel", "Wordpress",
        "UI/UX", "Logo Design", "Branding", "Illustration", "Photoshop", "Figma", "SEO", 
        "Content Writing", "Copywriting", "Translation", "Data Analysis", "Machine Learning"
    ]
    
    for tag_name in tags:
        Tag.objects.get_or_create(name=tag_name, slug=tag_name.lower().replace(" ", "-"))
    
    return Tag.objects.all()

# Создание пользователей - фрилансеров и клиентов
def create_users():
    # Создаем фрилансеров
    freelancers = []
    for i in range(1, 6):
        username = f"freelancer{i}"
        email = f"freelancer{i}@example.com"
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password="password123",
                first_name=f"Фрилансер{i}",
                last_name=f"Фамилия{i}",
                user_type="freelancer"
            )
            
            # Создаем профиль фрилансера
            profile = FreelancerProfile.objects.get(user=user)
            profile.portfolio_website = f"https://portfolio{i}.example.com"
            profile.rating = round(random.uniform(3.5, 5.0), 1)
            profile.is_available = random.choice([True, False])
            profile.experience_years = random.randint(1, 10)
            profile.education = f"Университет №{i}, Факультет Компьютерных Наук"
            profile.certifications = f"Сертификат {i} по веб-разработке"
            profile.languages = "Русский, Казахский, Английский"
            profile.specialization = random.choice(["Веб-разработка", "Мобильная разработка", "Дизайн"])
            profile.save()
            
            # Дополняем информацию пользователя
            user.skills = "Python, JavaScript, Django, HTML, CSS, SQL"
            user.hourly_rate = random.randint(10, 50) * 1000
            user.bio = f"Профессиональный разработчик с {profile.experience_years} годами опыта в сфере IT."
            user.save()
            
            freelancers.append(user)
        except:
            pass
    
    # Создаем клиентов
    clients = []
    for i in range(1, 4):
        username = f"client{i}"
        email = f"client{i}@example.com"
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password="password123",
                first_name=f"Клиент{i}",
                last_name=f"Фамилия{i}",
                user_type="client"
            )
            
            # Создаем профиль клиента
            profile = ClientProfile.objects.get(user=user)
            profile.company_website = f"https://company{i}.example.com"
            profile.industry = random.choice(["IT", "Финансы", "Образование", "Медицина"])
            profile.company_size = random.randint(5, 100)
            profile.save()
            
            # Дополняем информацию пользователя
            user.company_name = f"ООО Компания {i}"
            user.bio = f"Компания, специализирующаяся на {profile.industry}."
            user.save()
            
            clients.append(user)
        except:
            pass
    
    return freelancers, clients

# Создание портфолио для фрилансеров
def create_portfolios(freelancers, categories):
    for freelancer in freelancers:
        for i in range(1, random.randint(2, 5)):
            project = PortfolioProject.objects.create(
                freelancer=freelancer,
                title=f"Проект {i} в портфолио",
                description=f"Описание проекта {i} в портфолио фрилансера {freelancer.username}.",
                completed_date=timezone.now() - timedelta(days=random.randint(30, 365)),
                client_name=f"Клиент для портфолио {i}",
                url=f"https://portfolio-project{i}.example.com"
            )
            
            # Добавляем категории к проекту
            project.categories.add(random.choice(categories))

# Создание проектов
def create_projects(clients, categories, tags):
    projects = []
    
    for client in clients:
        for i in range(1, random.randint(3, 6)):
            budget_min = random.randint(50, 200) * 1000
            budget_max = budget_min + random.randint(50, 300) * 1000
            
            project = Project.objects.create(
                client=client,
                title=f"Проект {i} от {client.username}",
                description=f"Подробное описание проекта {i}. Требуется {random.choice(['разработка', 'дизайн', 'контент', 'маркетинг'])}.",
                category=random.choice(categories),
                budget_min=budget_min,
                budget_max=budget_max,
                budget_type=random.choice(["fixed", "hourly"]),
                deadline=timezone.now() + timedelta(days=random.randint(10, 60)),
                is_remote=random.choice([True, False]),
                experience_required=random.choice(["entry", "intermediate", "expert"])
            )
            
            # Добавляем теги к проекту
            for _ in range(random.randint(2, 5)):
                project.tags.add(random.choice(tags))
            
            projects.append(project)
    
    return projects

# Создание предложений на проекты
def create_proposals(freelancers, projects):
    proposals = []
    
    for project in projects:
        # Случайное количество предложений на проект
        num_proposals = random.randint(1, min(3, len(freelancers)))
        selected_freelancers = random.sample(freelancers, num_proposals)
        
        for freelancer in selected_freelancers:
            bid_amount = random.randint(
                int(project.budget_min),
                int(project.budget_max)
            )
            
            proposal = Proposal.objects.create(
                project=project,
                freelancer=freelancer,
                cover_letter=f"Предложение от {freelancer.username} на проект {project.title}. У меня есть опыт в подобных проектах.",
                bid_amount=bid_amount,
                delivery_time=random.randint(5, 30),
                status=random.choice(["pending", "accepted", "rejected"])
            )
            
            proposals.append(proposal)
    
    return proposals

# Создание контрактов на основе принятых предложений
def create_contracts(proposals):
    contracts = []
    
    for proposal in proposals:
        if proposal.status == "accepted":
            contract = Contract.objects.create(
                title=f"Контракт по проекту {proposal.project.title}",
                description=f"Контракт между {proposal.project.client.username} и {proposal.freelancer.username}",
                project=proposal.project,
                client=proposal.project.client,
                freelancer=proposal.freelancer,
                proposal=proposal,
                amount=proposal.bid_amount,
                deadline=proposal.project.deadline,
                status=random.choice(["active", "completed", "cancelled"])
            )
            
            # Создаем этапы для контракта
            num_milestones = random.randint(2, 4)
            milestone_amount = contract.amount / num_milestones
            
            for i in range(1, num_milestones + 1):
                days_offset = (i * contract.deadline.day) // num_milestones
                
                Milestone.objects.create(
                    contract=contract,
                    title=f"Этап {i} для {contract.title}",
                    description=f"Описание этапа {i} для контракта",
                    amount=milestone_amount,
                    due_date=timezone.now() + timedelta(days=days_offset),
                    status=random.choice(["pending", "submitted", "approved", "paid"])
                )
            
            contracts.append(contract)
    
    return contracts

# Создание кошельков и транзакций
def create_wallets_and_transactions(users):
    for user in users:
        wallet, created = Wallet.objects.get_or_create(user=user)
        
        # Создаем несколько транзакций для каждого пользователя
        for i in range(1, random.randint(3, 8)):
            amount = random.randint(50, 500) * 1000
            transaction_type = random.choice(["deposit", "withdrawal", "payment", "refund", "fee"])
            
            Transaction.objects.create(
                user=user,
                wallet=wallet,
                amount=amount,
                transaction_type=transaction_type,
                status="completed",
                description=f"{transaction_type.capitalize()} транзакция {i}",
            )
        
        # Обновляем баланс кошелька
        wallet.update_balance()

# Создание отзывов
def create_reviews(contracts):
    for contract in contracts:
        if contract.status == "completed":
            Review.objects.create(
                freelancer=contract.freelancer,
                client=contract.client,
                project=contract.project,
                rating=random.randint(3, 5),
                comment=f"Отзыв о работе фрилансера {contract.freelancer.username} на проекте {contract.project.title}. Работа выполнена качественно и в срок."
            )

# Главная функция
def create_test_data():
    print("Создание тестовых данных...")
    
    # Создаем базовые данные
    categories = create_categories()
    tags = create_tags()
    freelancers, clients = create_users()
    
    # Создаем портфолио для фрилансеров
    create_portfolios(freelancers, categories)
    
    # Создаем проекты, предложения и контракты
    projects = create_projects(clients, categories, tags)
    proposals = create_proposals(freelancers, projects)
    contracts = create_contracts(proposals)
    
    # Создаем финансовые данные и отзывы
    all_users = freelancers + clients
    create_wallets_and_transactions(all_users)
    create_reviews(contracts)
    
    print("Тестовые данные успешно созданы!")

if __name__ == "__main__":
    create_test_data() 