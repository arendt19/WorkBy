import os
import django
import sys

# u041du0430u0441u0442u0440u043eu0439u043au0430 u0441u0440u0435u0434u044b Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelance_core.settings')
django.setup()

# u0418u043cu043fu043eu0440u0442u044b
from django.core.management import call_command
from django.contrib.auth import get_user_model
from accounts.models import FreelancerProfile, ClientProfile

User = get_user_model()

def run_migrations():
    """\u0417\u0430\u043f\u0443\u0441\u043a \u043c\u0438\u0433\u0440\u0430\u0446\u0438\u0439"""
    print("\u0417\u0430\u043f\u0443\u0441\u043a \u043c\u0438\u0433\u0440\u0430\u0446\u0438\u0439...")
    call_command('migrate')
    
    print("\u041c\u0438\u0433\u0440\u0430\u0446\u0438\u0438 \u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u044b!")

def create_users():
    """\u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439"""
    print("\u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439...")
    
    # \u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u0441\u0443\u043f\u0435\u0440\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f
    if not User.objects.filter(username='arendt').exists():
        admin_user = User.objects.create_superuser(
            username='arendt',
            email='admin@example.com',
            password='password123'
        )
        print(f"\u0421\u043e\u0437\u0434\u0430\u043d \u0430\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u043e\u0440: {admin_user.username}")
    
    # \u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u0444\u0440\u0438\u043b\u0430\u043d\u0441\u0435\u0440\u0430
    if not User.objects.filter(username='freelancer2').exists():
        freelancer = User.objects.create_user(
            username='freelancer2',
            email='freelancer2@example.com',
            password='password123',
            first_name='\u0418\u0432\u0430\u043d',
            last_name='\u0424\u0440\u0438\u043b\u0430\u043d\u0441\u0435\u0440\u043e\u0432'
        )
        freelancer.user_type = 'freelancer'
        freelancer.save()
        
        # \u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u043f\u0440\u043e\u0444\u0438\u043b\u044f \u0444\u0440\u0438\u043b\u0430\u043d\u0441\u0435\u0440\u0430
        FreelancerProfile.objects.create(
            user=freelancer,
            bio="\u041e\u043f\u044b\u0442\u043d\u044b\u0439 \u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u0447\u0438\u043a \u0441 5+ \u043b\u0435\u0442 \u043e\u043f\u044b\u0442\u0430",
            specialization="\u0412\u0435\u0431-\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u0447\u0438\u043a Full Stack",
            experience_years=5,
            hourly_rate=3000,
            skills="Python, Django, JavaScript, React",
            location="\u0410\u043b\u043c\u0430\u0442\u044b, \u041a\u0430\u0437\u0430\u0445\u0441\u0442\u0430\u043d",
            is_available=True
        )
        print(f"\u0421\u043e\u0437\u0434\u0430\u043d \u0444\u0440\u0438\u043b\u0430\u043d\u0441\u0435\u0440: {freelancer.username}")
    
    # \u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u043a\u043b\u0438\u0435\u043d\u0442\u0430
    if not User.objects.filter(username='client2').exists():
        client = User.objects.create_user(
            username='client2',
            email='client2@example.com',
            password='password123',
            first_name='\u041f\u0435\u0442\u0440',
            last_name='\u0417\u0430\u043a\u0430\u0437\u0447\u0438\u043a\u043e\u0432'
        )
        client.user_type = 'client'
        client.save()
        
        # \u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u043f\u0440\u043e\u0444\u0438\u043b\u044f \u043a\u043b\u0438\u0435\u043d\u0442\u0430
        ClientProfile.objects.create(
            user=client,
            company_name="\u041e\u041e\u041e \u0422\u0435\u0445\u043d\u043e\u043b\u043e\u0433\u0438\u0438 \u0411\u0443\u0434\u0443\u0449\u0435\u0433\u043e",
            industry="IT \u0438 \u0442\u0435\u0445\u043d\u043e\u043b\u043e\u0433\u0438\u0438"
        )
        print(f"\u0421\u043e\u0437\u0434\u0430\u043d \u043a\u043b\u0438\u0435\u043d\u0442: {client.username}")

def load_initial_data():
    """\u0417\u0430\u0433\u0440\u0443\u0437\u043a\u0430 \u043d\u0430\u0447\u0430\u043b\u044c\u043d\u044b\u0445 \u0434\u0430\u043d\u043d\u044b\u0445"""
    print("\u0417\u0430\u0433\u0440\u0443\u0437\u043a\u0430 \u0434\u0430\u043d\u043d\u044b\u0445 \u0434\u043b\u044f \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0439 \u0438 \u0442\u0435\u0433\u043e\u0432...")
    try:
        # \u0417\u0430\u0433\u0440\u0443\u0437\u043a\u0430 \u0434\u0430\u043d\u043d\u044b\u0445 \u0434\u043b\u044f \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0439 \u0438 \u0442\u0435\u0433\u043e\u0432
        call_command('loaddata', 'jobs/fixtures/initial_categories.json')
        call_command('loaddata', 'jobs/fixtures/initial_tags.json')
        print("\u0414\u0430\u043d\u043d\u044b\u0435 \u0443\u0441\u043f\u0435\u0448\u043d\u043e \u0437\u0430\u0433\u0440\u0443\u0436\u0435\u043d\u044b")
    except Exception as e:
        print(f"\u041e\u0448\u0438\u0431\u043a\u0430 \u043f\u0440\u0438 \u0437\u0430\u0433\u0440\u0443\u0437\u043a\u0435 \u0434\u0430\u043d\u043d\u044b\u0445: {e}")

def main():
    """\u041e\u0441\u043d\u043e\u0432\u043d\u0430\u044f \u0444\u0443\u043d\u043a\u0446\u0438\u044f"""
    print("=== \u041c\u0438\u0433\u0440\u0430\u0446\u0438\u044f \u043d\u0430 PostgreSQL ===")
    
    # \u0417\u0430\u043f\u0443\u0441\u043a \u043c\u0438\u0433\u0440\u0430\u0446\u0438\u0439
    run_migrations()
    
    # \u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439
    create_users()
    
    # \u0417\u0430\u0433\u0440\u0443\u0437\u043a\u0430 \u043d\u0430\u0447\u0430\u043b\u044c\u043d\u044b\u0445 \u0434\u0430\u043d\u043d\u044b\u0445
    load_initial_data()
    
    print("=== \u041c\u0438\u0433\u0440\u0430\u0446\u0438\u044f \u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u0430 ===")

if __name__ == "__main__":
    main()
