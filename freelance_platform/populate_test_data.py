import os
import sys
import random
import django
from datetime import timedelta

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelance_core.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model
from jobs.models import Project, Category, Tag
from accounts.models import FreelancerProfile, ClientProfile
from payments.models import Wallet, Transaction

User = get_user_model()

# Список примерных названий проектов
project_titles = [
    "Разработка мобильного приложения для фитнес-тренировок",
    "Создание корпоративного веб-сайта для строительной компании",
    "Дизайн логотипа и фирменного стиля для стартапа",
    "Разработка API для интеграции платежной системы",
    "Создание онлайн-платформы для изучения иностранных языков",
    "Разработка игры на Unity для мобильных устройств",
    "Создание системы управления контентом для новостного сайта",
    "Разработка блога на WordPress с индивидуальным дизайном",
    "Создание презентации для инвестиционного проекта",
    "Разработка бота для Telegram с элементами ИИ",
    "Верстка электронного журнала для публикации онлайн",
    "Создание анимационного рекламного ролика для продукта"
]

# Списки для описаний проектов
intro_phrases = [
    "Мы ищем опытного разработчика для",
    "Требуется талантливый фрилансер для",
    "Наша компания заинтересована в специалисте для",
    "Ищем креативного исполнителя для",
    "Нужен профессионал с опытом для"
]

task_descriptions = [
    "создания современного и адаптивного дизайна",
    "разработки функционального и удобного интерфейса",
    "написания чистого и оптимизированного кода",
    "создания уникального и запоминающегося визуального решения",
    "разработки полнофункционального программного обеспечения",
    "создания интуитивно понятного пользовательского опыта",
    "разработки масштабируемой архитектуры"
]

tech_requirements = [
    "Знание HTML, CSS и JavaScript необходимо.",
    "Опыт работы с React/Vue/Angular будет большим плюсом.",
    "Требуется опыт работы с Python и Django.",
    "Знание принципов UX/UI дизайна обязательно.",
    "Необходимо владение Adobe Photoshop, Illustrator и Figma.",
    "Опыт разработки мобильных приложений на Flutter/React Native.",
    "Требуется знание SQL и опыт работы с базами данных.",
    "Опыт работы с AWS/Google Cloud/Azure приветствуется.",
    "Необходимы навыки верстки адаптивных макетов."
]

deliverables = [
    "исходный код в репозитории GitHub с документацией",
    "готовый продукт с возможностью внесения правок",
    "дизайн-макеты в формате PSD и готовые файлы для использования",
    "рабочее приложение, опубликованное в магазинах приложений",
    "настроенный и готовый к работе сервер с развернутым приложением"
]

def generate_project_description():
    """Генерирует случайное описание проекта"""
    intro = random.choice(intro_phrases)
    task = random.choice(task_descriptions)
    tech = random.choice(tech_requirements)
    deliverable = random.choice(deliverables)
    
    return f"{intro} {task}. {tech} Результатом должен быть {deliverable}."

def create_test_projects():
    """Создает тестовые проекты"""
    
    print("Создание тестовых проектов...")
    
    # Получаем категории и клиентов
    categories = list(Category.objects.all())
    clients = User.objects.filter(client_profile__isnull=False)
    tags = list(Tag.objects.all())
    
    if not categories:
        print("Ошибка: Нет доступных категорий. Пожалуйста, создайте категории перед запуском скрипта.")
        return
    
    if not clients:
        print("Ошибка: Нет доступных клиентов. Пожалуйста, создайте клиентов перед запуском скрипта.")
        return
    
    # Создаем проекты
    created_projects = 0
    for title in project_titles:
        if Project.objects.filter(title=title).exists():
            print(f"Проект '{title}' уже существует, пропускаем...")
            continue
            
        # Случайные значения для проекта
        client = random.choice(clients)
        category = random.choice(categories)
        description = generate_project_description()
        budget_min = random.choice([100, 200, 300, 500, 750, 1000])
        budget_max = budget_min + random.choice([100, 200, 300, 500, 750, 1000])
        days_to_deadline = random.choice([7, 14, 30, 60])
        
        # Тип бюджета
        budget_type = random.choice(['fixed', 'hourly'])
        
        # Создаем проект
        created_date = timezone.now() - timedelta(days=random.randint(1, 30))
        
        project = Project.objects.create(
            title=title,
            client=client,
            category=category,
            description=description,
            budget_type=budget_type,
            budget_min=budget_min,
            budget_max=budget_max,
            deadline=timezone.now() + timedelta(days=days_to_deadline),
            status='open',
            created_at=created_date,
            is_remote=True
        )
        
        # Добавляем случайные теги к проекту (от 1 до 4)
        project_tags = random.sample(tags, min(random.randint(1, 4), len(tags)))
        project.tags.set(project_tags)
        
        print(f"Создан проект: {title}")
        created_projects += 1
    
    print(f"Всего создано {created_projects} новых проектов.")

def add_balance_to_accounts():
    """Добавляет баланс 10000 на все кошельки пользователей"""
    
    print("Добавление баланса на кошельки пользователей...")
    
    users = User.objects.all()
    for user in users:
        wallet, created = Wallet.objects.get_or_create(user=user)
        
        # Добавляем средства на баланс
        if wallet.balance < 10000:
            amount_to_add = 10000 - wallet.balance
            
            # Обновляем баланс кошелька
            wallet.balance = 10000
            wallet.save()
            
            # Создаем транзакцию вручную для пополнения
            Transaction.objects.create(
                user=user,
                amount=amount_to_add,
                transaction_type='deposit',
                status='completed',
                description='Тестовое пополнение баланса'
            )
            
            print(f"Баланс пользователя {user.username} пополнен до 10000")
        else:
            print(f"У пользователя {user.username} уже достаточно средств (текущий баланс: {wallet.balance})")


if __name__ == "__main__":
    print("Начинаем заполнение тестовыми данными...")
    create_test_projects()
    add_balance_to_accounts()
    print("Заполнение тестовыми данными завершено!")
