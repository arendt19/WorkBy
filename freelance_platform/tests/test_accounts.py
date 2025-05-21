from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import FreelancerProfile, ClientProfile


class AccountsTest(TestCase):
    """Тесты для приложения accounts"""
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='freelancer'
        )
        
    def test_user_profile_creation(self):
        """Тест автоматического создания профиля пользователя"""
        # В зависимости от типа пользователя проверяем соответствующий профиль
        if self.user.is_freelancer:
            profile = FreelancerProfile.objects.get(user=self.user)
        else:
            profile = ClientProfile.objects.get(user=self.user)
            
        self.assertIsNotNone(profile)
        self.assertEqual(profile.user, self.user)
        
    def test_user_login(self):
        """Тест входа пользователя в систему"""
        response = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)  # Редирект после успешного входа 