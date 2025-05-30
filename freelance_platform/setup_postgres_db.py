import os
import django
import sys

# u041du0430u0441u0442u0440u043eu0439u043au0430 Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelance_core.settings')
django.setup()

# u0418u043cu043fu043eu0440u0442u044b
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.db import connection
from accounts.models import FreelancerProfile, ClientProfile
from jobs.models import Category, Tag, Project

User = get_user_model()

def setup_database():
    """u041du0430u0441u0442u0440u043eu0439u043au0430 u0431u0430u0437u044b u0434u0430u043du043du044bu0445 PostgreSQL"""
    print("u041fu0440u043eu0432u0435u0440u043au0430 u0441u043eu0435u0434u0438u043du0435u043du0438u044f u0441 PostgreSQL...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()[0]
            print(f"u0423u0441u043fu0435u0448u043du043eu0435 u043fu043eu0434u043au043bu044eu0447u0435u043du0438u0435 u043a PostgreSQL: {db_version}")
    except Exception as e:
        print(f"u041eu0448u0438u0431u043au0430 u043fu043eu0434u043au043bu044eu0447u0435u043du0438u044f u043a PostgreSQL: {e}")
        print("u0423u0431u0435u0434u0438u0442u0435u0441u044c, u0447u0442u043e u0432 pgAdmin u0441u043eu0437u0434u0430u043du0430 u0431u0430u0437u0430 u0434u0430u043du043du044bu0445 'freelance_db'")
        sys.exit(1)
    
    # u0417u0430u043fu0443u0441u043a u043cu0438u0433u0440u0430u0446u0438u0439
    print("u0417u0430u043fu0443u0441u043a u043cu0438u0433u0440u0430u0446u0438u0439...")
    call_command('migrate')
    
    # u0421u043eu0437u0434u0430u043du0438u0435 u0441u0443u043fu0435u0440u043fu043eu043bu044cu0437u043eu0432u0430u0442u0435u043bu044f
    print("u0421u043eu0437u0434u0430u043du0438u0435 u0441u0443u043fu0435u0440u043fu043eu043bu044cu0437u043eu0432u0430u0442u0435u043bu044f...")
    if not User.objects.filter(username='arendt').exists():
        admin_user = User.objects.create_superuser(
            username='arendt',
            email='admin@example.com',
            password='password123'
        )
        print(f"u0421u043eu0437u0434u0430u043d u0441u0443u043fu0435u0440u043fu043eu043bu044cu0437u043eu0432u0430u0442u0435u043bu044c: {admin_user.username}")
    else:
        print("u0421u0443u043fu0435u0440u043fu043eu043bu044cu0437u043eu0432u0430u0442u0435u043bu044c 'arendt' u0443u0436u0435 u0441u0443u0449u0435u0441u0442u0432u0443u0435u0442")
    
    # u0421u043eu0437u0434u0430u043du0438u0435 u0444u0440u0438u043bu0430u043du0441u0435u0440u0430
    print("u0421u043eu0437u0434u0430u043du0438u0435 u0442u0435u0441u0442u043eu0432u043eu0433u043e u0444u0440u0438u043bu0430u043du0441u0435u0440u0430...")
    if not User.objects.filter(username='freelancer2').exists():
        freelancer = User.objects.create_user(
            username='freelancer2',
            email='freelancer2@example.com',
            password='password123',
            first_name='u0418u0432u0430u043d',
            last_name='u0424u0440u0438u043bu0430u043du0441u0435u0440u043eu0432'
        )
        freelancer.user_type = 'freelancer'
        freelancer.save()
        
        # u0421u043eu0437u0434u0430u043du0438u0435 u043fu0440u043eu0444u0438u043bu044f u0444u0440u0438u043bu0430u043du0441u0435u0440u0430
        FreelancerProfile.objects.create(
            user=freelancer,
            bio="u041eu043fu044bu0442u043du044bu0439 u0440u0430u0437u0440u0430u0431u043eu0442u0447u0438u043a u0441 5+ u043bu0435u0442 u043eu043fu044bu0442u0430",
            specialization="u0412u0435u0431-u0440u0430u0437u0440u0430u0431u043eu0442u0447u0438u043a Full Stack",
            experience_years=5,
            hourly_rate=3000,
            skills="Python, Django, JavaScript, React",
            location="u0410u043bu043cu0430u0442u044b, u041au0430u0437u0430u0445u0441u0442u0430u043d",
            is_available=True
        )
        print(f"u0421u043eu0437u0434u0430u043d u0444u0440u0438u043bu0430u043du0441u0435u0440: {freelancer.username}")
    else:
        print("u0424u0440u0438u043bu0430u043du0441u0435u0440 'freelancer2' u0443u0436u0435 u0441u0443u0449u0435u0441u0442u0432u0443u0435u0442")
    
    # u0421u043eu0437u0434u0430u043du0438u0435 u043au043bu0438u0435u043du0442u0430
    print("u0421u043eu0437u0434u0430u043du0438u0435 u0442u0435u0441u0442u043eu0432u043eu0433u043e u043au043bu0438u0435u043du0442u0430...")
    if not User.objects.filter(username='client2').exists():
        client = User.objects.create_user(
            username='client2',
            email='client2@example.com',
            password='password123',
            first_name='u041fu0435u0442u0440',
            last_name='u0417u0430u043au0430u0437u0447u0438u043au043eu0432'
        )
        client.user_type = 'client'
        client.save()
        
        # u0421u043eu0437u0434u0430u043du0438u0435 u043fu0440u043eu0444u0438u043bu044f u043au043bu0438u0435u043du0442u0430
        ClientProfile.objects.create(
            user=client,
            company_name="u041eu041eu041e u0422u0435u0445u043du043eu043bu043eu0433u0438u0438 u0411u0443u0434u0443u0449u0435u0433u043e",
            industry="IT u0438 u0442u0435u0445u043du043eu043bu043eu0433u0438u0438"
        )
        print(f"u0421u043eu0437u0434u0430u043d u043au043bu0438u0435u043du0442: {client.username}")
    else:
        print("u041au043bu0438u0435u043du0442 'client2' u0443u0436u0435 u0441u0443u0449u0435u0441u0442u0432u0443u0435u0442")
    
    # u0417u0430u0433u0440u0443u0437u043au0430 u0444u0438u043au0441u0442u0443u0440 u0434u043bu044f u043au0430u0442u0435u0433u043eu0440u0438u0439 u0438 u0442u0435u0433u043eu0432
    print("u0417u0430u0433u0440u0443u0437u043au0430 u043au0430u0442u0435u0433u043eu0440u0438u0439 u0438 u0442u0435u0433u043eu0432...")
    try:
        call_command('loaddata', 'jobs/fixtures/initial_categories.json')
        call_command('loaddata', 'jobs/fixtures/initial_tags.json')
        print("u041au0430u0442u0435u0433u043eu0440u0438u0438 u0438 u0442u0435u0433u0438 u0443u0441u043fu0435u0448u043du043e u0437u0430u0433u0440u0443u0436u0435u043du044b")
    except Exception as e:
        print(f"u041eu0448u0438u0431u043au0430 u043fu0440u0438 u0437u0430u0433u0440u0443u0437u043au0435 u0444u0438u043au0441u0442u0443u0440: {e}")
    
    print("u041du0430u0441u0442u0440u043eu0439u043au0430 u0431u0430u0437u044b u0434u0430u043du043du044bu0445 PostgreSQL u0437u0430u0432u0435u0440u0448u0435u043du0430!")

if __name__ == "__main__":
    setup_database()
