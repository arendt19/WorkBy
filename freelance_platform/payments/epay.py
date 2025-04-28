import hashlib
import json
import uuid
import requests
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class EpayAPI:
    """
    Класс для работы с API платежной системы Epay от Halyk Bank
    """
    
    def __init__(self, transaction_type='payment'):
        """
        Инициализация с выбором типа транзакции
        """
        if transaction_type == 'payment':
            # Данные для оплаты
            self.client_id = 'test'
            self.client_secret = 'yF587AV9Ms94qN2QShFzVR3vFnWkhjbAK3sG'
            self.terminal_id = '67e34d63-102f-4bd1-898e-370781d0074d'
        elif transaction_type == 'p2p':
            # Данные для P2P переводов
            self.client_id = 'test'
            self.client_secret = 'yF587AV9Ms94qN2QShFzVR3vFnWkhjbAK3sG'
            self.terminal_id = '40a348cb-68a3-45d5-9002-a4836d79c3b5'
        elif transaction_type == 'oct':
            # Данные для выплат
            self.client_id = 'test'
            self.client_secret = 'yF587AV9Ms94qN2QShFzVR3vFnWkhjbAK3sG'
            self.terminal_id = 'c36b282f-6819-4d4f-85df-a4bdc8a8f703'
        elif transaction_type == 'link':
            # Данные для ссылки на оплату
            self.client_id = 'halykfinanceUSD'
            self.client_secret = 'U01gQZVL##lJ$NhJ'
            self.shop_id = '04f25a4b-d2bd-4dd8-b3a7-9390be4774c4'
            
        # Базовый URL API
        self.api_url = 'https://testpay.kkb.kz/epay2'
        
    def generate_signature(self, data):
        """
        Генерация подписи для запроса
        """
        # Сортировка ключей и преобразование в JSON строку
        sorted_data = json.dumps(data, sort_keys=True, separators=(',', ':'))
        # Создание подписи с использованием HMAC-SHA256
        signature = hashlib.sha256((sorted_data + self.client_secret).encode()).hexdigest()
        return signature
    
    def create_payment(self, amount, currency, description, order_id=None, return_url=None, callback_url=None):
        """
        Создание платежа
        """
        if not order_id:
            order_id = str(uuid.uuid4())
            
        # Подготовка данных запроса
        data = {
            'amount': float(amount),
            'currency': currency,
            'description': description,
            'orderId': order_id,
            'terminalId': self.terminal_id,
            'clientId': self.client_id
        }
        
        if return_url:
            data['returnUrl'] = return_url
            
        if callback_url:
            data['callbackUrl'] = callback_url
            
        # Добавление подписи
        data['signature'] = self.generate_signature(data)
        
        # Отправка запроса
        response = requests.post(
            f"{self.api_url}/payment",
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        
        return response.json()
    
    def create_payment_link(self, amount, currency, description, order_id=None):
        """
        Создание ссылки на оплату
        """
        if not order_id:
            order_id = str(uuid.uuid4())
            
        # Подготовка данных запроса
        data = {
            'amount': float(amount),
            'currency': currency,
            'description': description,
            'orderId': order_id,
            'shopId': self.shop_id,
            'clientId': self.client_id
        }
        
        # Добавление подписи
        data['signature'] = self.generate_signature(data)
        
        # Отправка запроса
        response = requests.post(
            f"{self.api_url}/link",
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        
        return response.json()
    
    def p2p_transfer(self, amount, currency, sender_card, recipient_card, description, order_id=None):
        """
        Перевод средств между картами (P2P)
        """
        if not order_id:
            order_id = str(uuid.uuid4())
            
        # Подготовка данных запроса
        data = {
            'amount': float(amount),
            'currency': currency,
            'description': description,
            'orderId': order_id,
            'terminalId': self.terminal_id,
            'clientId': self.client_id,
            'sender': {
                'pan': sender_card,
                'expDate': '01/27',
                'cvc': '123'
            },
            'recipient': {
                'pan': recipient_card
            }
        }
        
        # Добавление подписи
        data['signature'] = self.generate_signature(data)
        
        # Отправка запроса
        response = requests.post(
            f"{self.api_url}/p2p",
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        
        return response.json()
    
    def verify_callback(self, data, signature):
        """
        Проверка подписи callback от Epay
        """
        calculated_signature = self.generate_signature(data)
        return calculated_signature == signature

    def get_payment_status(self, payment_id):
        """
        Получение статуса платежа
        """
        data = {
            'paymentId': payment_id,
            'clientId': self.client_id,
            'terminalId': self.terminal_id
        }
        
        # Добавление подписи
        data['signature'] = self.generate_signature(data)
        
        # Отправка запроса
        response = requests.post(
            f"{self.api_url}/status",
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        
        return response.json() 