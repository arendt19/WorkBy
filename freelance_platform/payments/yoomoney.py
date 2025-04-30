import requests
import uuid
import hmac
import hashlib
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class YooMoneyAPI:
    """
    Класс для работы с API YooMoney
    """
    def __init__(self):
        self.base_url = 'https://api.yoomoney.ru/v3'
        self.client_id = settings.YOOMONEY_SETTINGS['CLIENT_ID']
        self.client_secret = settings.YOOMONEY_SETTINGS['CLIENT_SECRET']
        self.redirect_uri = settings.YOOMONEY_SETTINGS['REDIRECT_URI']
        self.notification_uri = settings.YOOMONEY_SETTINGS['NOTIFICATION_URI']
    
    def get_auth_headers(self):
        """
        Возвращает заголовки аутентификации для запросов к API
        """
        return {
            'Authorization': f'Bearer {self.client_secret}',
            'Content-Type': 'application/json'
        }
    
    def create_payment(self, amount, return_url=None, description=None, metadata=None):
        """
        Создает новый платеж
        """
        if not return_url:
            return_url = self.redirect_uri
        
        if not description:
            description = _("Payment to WorkBy")
        
        # Создаем уникальный идентификатор платежа
        payment_id = str(uuid.uuid4())
        
        # Формируем данные для запроса
        payment_data = {
            'amount': {
                'value': str(amount),
                'currency': 'KZT'
            },
            'confirmation': {
                'type': 'redirect',
                'return_url': return_url
            },
            'capture': True,
            'description': description[:128],  # Ограничение YooMoney
            'metadata': metadata or {
                'payment_id': payment_id
            }
        }
        
        # Добавляем уведомление о платеже, если настроено
        if self.notification_uri:
            payment_data['webhook'] = {
                'url': self.notification_uri,
                'event_types': ['payment.succeeded', 'payment.canceled']
            }
        
        # Отправляем запрос к API
        response = requests.post(
            f'{self.base_url}/payments',
            headers=self.get_auth_headers(),
            json=payment_data
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            try:
                error_data = response.json()
                error_message = error_data.get('message', 'Unknown error')
            except:
                error_message = f'Failed to initiate payment. Status: {response.status_code}'
            
            raise Exception(error_message)
    
    def get_payment_status(self, payment_id):
        """
        Проверяет статус платежа
        """
        response = requests.get(
            f'{self.base_url}/payments/{payment_id}',
            headers=self.get_auth_headers()
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            try:
                error_data = response.json()
                error_message = error_data.get('message', 'Unknown error')
            except:
                error_message = f'Failed to get payment status. Status: {response.status_code}'
            
            raise Exception(error_message)
    
    def verify_notification(self, notification_data, signature):
        """
        Проверяет подпись уведомления от YooMoney
        """
        if not signature:
            return False
        
        # Вычисляем ожидаемую подпись
        expected_signature = hmac.new(
            self.client_secret.encode(),
            notification_data.encode(),
            hashlib.sha1
        ).hexdigest()
        
        return signature == expected_signature
    
    def process_succeeded_payment(self, payment_info):
        """
        Обрабатывает успешный платеж
        """
        # Получаем данные из платежа
        metadata = payment_info.get('metadata', {})
        amount = payment_info['amount']['value']
        
        return {
            'status': 'succeeded',
            'amount': amount,
            'metadata': metadata
        } 