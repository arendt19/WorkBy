import os
import django

# u041du0430u0441u0442u0440u043eu0439u043au0430 Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelance_core.settings')
django.setup()

# u0418u043cu043fu043eu0440u0442u044b
from django.contrib.auth import get_user_model
from accounts.models import FreelancerProfile, ClientProfile

User = get_user_model()

def create_test_users():
    print("u0421u043eu0437u0434u0430u043du0438u0435 u0442u0435u0441u0442u043eu0432u044bu0445 u043fu043eu043bu044cu0437u043eu0432u0430u0442u0435u043bu0435u0439...")
    
    # 1. u0421u0443u043fu0435u0440u043fu043eu043bu044cu0437u043eu0432u0430u0442u0435u043bu044c (u0430u0434u043cu0438u043du0438u0441u0442u0440u0430u0442u043eu0440)
    if not User.objects.filter(username='arendt').exists():
        admin = User.objects.create_superuser(
            username='arendt',
            email='admin@example.com',
            password='password123',
            first_name='u0410u0434u043cu0438u043d',
            last_name='u0410u0434u043cu0438u043du043eu0432'
        )
        print(f"u0421u043eu0437u0434u0430u043d u0441u0443u043fu0435u0440u043fu043eu043bu044cu0437u043eu0432u0430u0442u0435u043bu044c: {admin.username}")
    else:
        print("u0421u0443u043fu0435u0440u043fu043eu043bu044cu0437u043eu0432u0430u0442u0435u043bu044c 'arendt' u0443u0436u0435 u0441u0443u0449u0435u0441u0442u0432u0443u0435u0442")
    
    # 2. u0424u0440u0438u043bu0430u043du0441u0435u0440
    if not User.objects.filter(username='freelancer2').exists():
        freelancer = User.objects.create_user(
            username='freelancer2',
            email='freelancer2@example.com',
            password='password123',
            first_name='\u0418\u0432\u0430\u043d',
            last_name='\u0424\u0440\u0438\u043b\u0430\u043d\u0441\u0435\u0440\u043e\u0432',
            user_type='freelancer',
            bio="\u041e\u043f\u044b\u0442\u043d\u044b\u0439 \u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u0447\u0438\u043a \u0441 5+ \u043b\u0435\u0442 \u043e\u043f\u044b\u0442\u0430",
            skills="Python, Django, JavaScript, React",
            hourly_rate=3000
        )
        
        # u0421u043eu0437u0434u0430u043du0438u0435 u043fu0440u043eu0444u0438u043bu044f u0444u0440u0438u043bu0430u043du0441u0435u0440u0430
        FreelancerProfile.objects.create(
            user=freelancer,
            specialization="\u0412\u0435\u0431-\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u0447\u0438\u043a Full Stack",
            experience_years=5,
            languages="\u0420\u0443\u0441\u0441\u043a\u0438\u0439, \u0410\u043d\u0433\u043b\u0438\u0439\u0441\u043a\u0438\u0439",
            is_available=True
        )
        print(f"u0421u043eu0437u0434u0430u043du u0444u0440u0438u043bu0430u043du0441u0435u0440: {freelancer.username}")
    else:
        print("u0424u0440u0438u043bu0430u043du0441u0435u0440 'freelancer2' u0443u0436u0435 u0441u0443u0449u0435u0441u0442u0432u0443u0435u0442")
    
    # 3. u041au043bu0438u0435u043du0442
    if not User.objects.filter(username='client2').exists():
        client = User.objects.create_user(
            username='client2',
            email='client2@example.com',
            password='password123',
            first_name='\u041f\u0435\u0442\u0440',
            last_name='\u0417\u0430\u043a\u0430\u0437\u0447\u0438\u043a\u043e\u0432',
            user_type='client',
            company_name="\u041e\u041e\u041e \u0422\u0435\u0445\u043d\u043e\u043b\u043e\u0433\u0438\u0438 \u0411\u0443\u0434\u0443\u0449\u0435\u0433\u043e"
        )
        
        # \u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u043f\u0440\u043e\u0444\u0438\u043b\u044f \u043a\u043b\u0438\u0435\u043d\u0442\u0430
        ClientProfile.objects.create(
            user=client,
            industry="IT \u0438 \u0442\u0435\u0445\u043d\u043e\u043b\u043e\u0433\u0438\u0438"
        )
        print(f"u0421u043eu0437u0434u0430u043du u043au043bu0438u0435u043du0442: {client.username}")
    else:
        print("u041au043bu0438u0435u043du0442 'client2' u0443u0436u0435 u0441u0443u0449u0435u0441u0442u0432u0443u0435u0442")

if __name__ == "__main__":
    create_test_users()
