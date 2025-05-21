from django.core.management.base import BaseCommand
from jobs.models import Category

class Command(BaseCommand):
    help = 'Creates default job categories'

    def handle(self, *args, **options):
        categories = [
            {
                'name': 'Web Development', 
                'name_ru': 'Веб-разработка', 
                'name_kk': 'Веб-әзірлеу',
                'description': 'Development of websites and web applications'
            },
            {
                'name': 'Mobile App Development', 
                'name_ru': 'Разработка мобильных приложений', 
                'name_kk': 'Мобильді қосымшаларды әзірлеу',
                'description': 'Development of mobile applications for iOS and Android'
            },
            {
                'name': 'Graphic Design', 
                'name_ru': 'Графический дизайн', 
                'name_kk': 'Графикалық дизайн',
                'description': 'Design of visual content for branding and marketing'
            },
            {
                'name': 'Content Writing', 
                'name_ru': 'Написание контента', 
                'name_kk': 'Контент жазу',
                'description': 'Writing of articles, blogs, and other content'
            },
            {
                'name': 'Digital Marketing', 
                'name_ru': 'Цифровой маркетинг', 
                'name_kk': 'Цифрлық маркетинг',
                'description': 'Marketing of products and services using digital technologies'
            },
            {
                'name': 'Video Production', 
                'name_ru': 'Видеопроизводство', 
                'name_kk': 'Бейне өндірісі',
                'description': 'Production of videos for various purposes'
            },
            {
                'name': 'Translation', 
                'name_ru': 'Перевод', 
                'name_kk': 'Аударма',
                'description': 'Translation of content between languages'
            },
            {
                'name': 'Data Science', 
                'name_ru': 'Наука о данных', 
                'name_kk': 'Деректер ғылымы',
                'description': 'Analysis of data to extract meaningful insights'
            },
            {
                'name': 'UI/UX Design', 
                'name_ru': 'UI/UX дизайн', 
                'name_kk': 'UI/UX дизайн',
                'description': 'Design of user interfaces and experiences'
            },
            {
                'name': 'Backend Development', 
                'name_ru': 'Бэкенд-разработка', 
                'name_kk': 'Бэкенд әзірлеу',
                'description': 'Development of server-side applications'
            },
            {
                'name': 'Frontend Development', 
                'name_ru': 'Фронтенд-разработка', 
                'name_kk': 'Фронтенд әзірлеу',
                'description': 'Development of client-side applications'
            },
            {
                'name': 'DevOps', 
                'name_ru': 'DevOps', 
                'name_kk': 'DevOps',
                'description': 'Combining software development with IT operations'
            },
            {
                'name': 'Game Development', 
                'name_ru': 'Разработка игр', 
                'name_kk': 'Ойын әзірлеу',
                'description': 'Development of video games'
            },
            {
                'name': 'AI & Machine Learning', 
                'name_ru': 'ИИ и машинное обучение', 
                'name_kk': 'ЖИ және машиналық оқыту',
                'description': 'Development of artificial intelligence and machine learning solutions'
            },
            {
                'name': 'Blockchain', 
                'name_ru': 'Блокчейн', 
                'name_kk': 'Блокчейн',
                'description': 'Development of blockchain-based solutions'
            },
            {
                'name': 'E-commerce Development', 
                'name_ru': 'Разработка электронной коммерции', 
                'name_kk': 'Электронды коммерция әзірлеу',
                'description': 'Development of online stores'
            },
            {
                'name': 'Legal Services', 
                'name_ru': 'Юридические услуги', 
                'name_kk': 'Заңды қызметтер',
                'description': 'Provision of legal services'
            },
            {
                'name': 'Financial Services', 
                'name_ru': 'Финансовые услуги', 
                'name_kk': 'Қаржылық қызметтер',
                'description': 'Provision of financial services'
            },
            {
                'name': 'Business Consulting', 
                'name_ru': 'Бизнес-консалтинг', 
                'name_kk': 'Бизнес-консалтинг',
                'description': 'Consulting for business strategy and operations'
            },
            {
                'name': 'Accounting & Bookkeeping', 
                'name_ru': 'Бухгалтерский учет', 
                'name_kk': 'Бухгалтерлік есеп',
                'description': 'Management of financial records'
            },
        ]
        
        for category_data in categories:
            category, created = Category.objects.get_or_create(name=category_data['name'], defaults=category_data)
            
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created category: {category.name}"))
            else:
                # Обновляем поля перевода даже для существующих категорий
                category.name_ru = category_data['name_ru']
                category.name_kk = category_data['name_kk']
                category.save()
                self.stdout.write(self.style.WARNING(f"Updated category: {category.name}"))
        
        self.stdout.write(self.style.SUCCESS('Default categories created successfully!')) 