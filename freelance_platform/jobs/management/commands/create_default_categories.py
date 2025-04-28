from django.core.management.base import BaseCommand
from jobs.models import Category

class Command(BaseCommand):
    help = 'Creates default job categories'

    def handle(self, *args, **options):
        categories = [
            {'name': 'Web Development', 'description': 'Development of websites and web applications'},
            {'name': 'Mobile App Development', 'description': 'Development of mobile applications for iOS and Android'},
            {'name': 'Graphic Design', 'description': 'Design of visual content for branding and marketing'},
            {'name': 'Content Writing', 'description': 'Writing of articles, blogs, and other content'},
            {'name': 'Digital Marketing', 'description': 'Marketing of products and services using digital technologies'},
            {'name': 'Video Production', 'description': 'Production of videos for various purposes'},
            {'name': 'Translation', 'description': 'Translation of content between languages'},
            {'name': 'Data Science', 'description': 'Analysis of data to extract meaningful insights'},
            {'name': 'UI/UX Design', 'description': 'Design of user interfaces and experiences'},
            {'name': 'Backend Development', 'description': 'Development of server-side applications'},
            {'name': 'Frontend Development', 'description': 'Development of client-side applications'},
            {'name': 'DevOps', 'description': 'Combining software development with IT operations'},
            {'name': 'Game Development', 'description': 'Development of video games'},
            {'name': 'AI & Machine Learning', 'description': 'Development of artificial intelligence and machine learning solutions'},
            {'name': 'Blockchain', 'description': 'Development of blockchain-based solutions'},
            {'name': 'E-commerce Development', 'description': 'Development of online stores'},
            {'name': 'Legal Services', 'description': 'Provision of legal services'},
            {'name': 'Financial Services', 'description': 'Provision of financial services'},
            {'name': 'Business Consulting', 'description': 'Consulting for business strategy and operations'},
            {'name': 'Accounting & Bookkeeping', 'description': 'Management of financial records'},
        ]
        
        for category_data in categories:
            category, created = Category.objects.get_or_create(name=category_data['name'], defaults=category_data)
            
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created category: {category.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Category already exists: {category.name}"))
        
        self.stdout.write(self.style.SUCCESS('Default categories created successfully!')) 