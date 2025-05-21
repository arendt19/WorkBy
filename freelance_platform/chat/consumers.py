import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Conversation, Message, Notification
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        
        # Проверяем, что пользователь аутентифицирован
        if self.scope['user'].is_anonymous:
            await self.close()
            return
        
        # Проверяем, что пользователь является участником беседы
        if not await self.is_conversation_member():
            await self.close()
            return
        
        # Присоединение к группе комнаты
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Покидание группы комнаты
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    # Получение сообщения от WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        # Сохраняем сообщение в базе данных
        message_obj = await self.save_message(message)
        
        # Отправка сообщения в группу комнаты
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': self.scope['user'].id,
                'sender_username': self.scope['user'].username,
                'timestamp': message_obj['timestamp'].isoformat(),
                'message_id': message_obj['id']
            }
        )
    
    # Получение сообщения из группы комнаты
    async def chat_message(self, event):
        # Отправка сообщения в WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id']
        }))
    
    @database_sync_to_async
    def is_conversation_member(self):
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            return conversation.participants.filter(id=self.scope['user'].id).exists()
        except Conversation.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, content):
        conversation = Conversation.objects.get(id=self.conversation_id)
        message = Message.objects.create(
            conversation=conversation,
            sender=self.scope['user'],
            content=content
        )
        
        # Создаем уведомление для получателя
        Notification.create_message_notification(message)
        
        # Обновляем время последнего обновления разговора
        conversation.updated_at = timezone.now()
        conversation.save()
        
        return {
            'id': message.id,
            'timestamp': message.created_at
        } 