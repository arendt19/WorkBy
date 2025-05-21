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
        
        # Проверяем наличие настроек YooMoney
        if not hasattr(settings, 'YOOMONEY_SETTINGS'):
            raise Exception('YOOMONEY_SETTINGS not found in your settings.py')
        
        yoomoney_settings = getattr(settings, 'YOOMONEY_SETTINGS', {})
        self.client_id = yoomoney_settings.get('CLIENT_ID', '')
        self.client_secret = yoomoney_settings.get('CLIENT_SECRET', '')
        self.redirect_uri = yoomoney_settings.get('REDIRECT_URI', '')
        self.notification_uri = yoomoney_settings.get('NOTIFICATION_URI', '')
        
        # Проверяем, что обязательные параметры заданы
        if not (self.client_id and self.client_secret):
            raise ValueError('YooMoney CLIENT_ID and CLIENT_SECRET must be set in your settings')
    
    def get_auth_headers(self):
        """
        Возвращает заголовки аутентификации для запросов к API
        """
        return {
            'Authorization': f'Bearer {self.client_secret}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
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
                'value': str(float(amount)),  # Преобразуем в строку обязательно через float
                'currency': 'KZT'
            },
            'confirmation': {
                'type': 'redirect',
                'return_url': return_url
            },
            'capture': True,
            'description': str(description)[:128],  # Ограничение YooMoney
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
        
        try:
            # Отправляем запрос к API
            response = requests.post(
                f'{self.base_url}/payments',
                headers=self.get_auth_headers(),
                json=payment_data,
                timeout=10  # Добавляем таймаут для запроса
            )
            
            response.raise_for_status()  # Вызывает исключение при ошибках HTTP
            
            return response.json()
        except requests.exceptions.RequestException as e:
            error_message = f'Failed to connect to YooMoney API: {str(e)}'
            if hasattr(e, 'response') and e.response:
                try:
                    error_data = e.response.json()
                    error_message = f"YooMoney API error: {error_data.get('description', error_data.get('message', str(e)))}"
                except:
                    error_message = f'YooMoney API error: {e.response.status_code} {e.response.reason}'
            
            raise Exception(error_message)
    
    def get_payment_status(self, payment_id):
        """
        Проверяет статус платежа
        """
        try:
            response = requests.get(
                f'{self.base_url}/payments/{payment_id}',
                headers=self.get_auth_headers(),
                timeout=10  # Добавляем таймаут для запроса
            )
            
            response.raise_for_status()  # Вызывает исключение при ошибках HTTP
            
            return response.json()
        except requests.exceptions.RequestException as e:
            error_message = f'Failed to get payment status: {str(e)}'
            if hasattr(e, 'response') and e.response:
                try:
                    error_data = e.response.json()
                    error_message = f"YooMoney API error: {error_data.get('description', error_data.get('message', str(e)))}"
                except:
                    error_message = f'YooMoney API error: {e.response.status_code} {e.response.reason}'
            
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
        amount_data = payment_info.get('amount', {})
        amount = amount_data.get('value', '0')
        
        return {
            'status': 'succeeded',
            'amount': amount,
            'metadata': metadata,
            'payment_id': payment_info.get('id'),
            'created_at': payment_info.get('created_at')
        } 